from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, send_file, Response
from ldap3 import Server, Connection, ALL_ATTRIBUTES, SUBTREE
import integration
from notification import get_user_notifications, get_db_connection
import csv
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from io import BytesIO, TextIOWrapper
import uuid
import asyncio
import json
import os
import unicodedata
import re
from unidecode import unidecode
from server.errorLog import get_error_logs

app = Flask(__name__)
app.secret_key = 'calvo'

def remover_acentos(texto):
    # Remove acentos e converte ç para c
    return unidecode(texto)

def get_user_session_file():
    # Gera um caminho para o arquivo de cache com base no UUID do usuário
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    user_id = session['user_id']
    file_path = os.path.join('cache', f"{user_id}.json")

    # Cria o arquivo temporário se não existir
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump([], file)

    return file_path

def authenticate(username, password):
    domain = 'digitalup.intranet'
    server = Server(domain, get_info=ALL_ATTRIBUTES)
    user = f'{username}@{domain}'
    conn = Connection(server, user=user, password=password)

    try:
        if conn.bind():
            # Pesquisa pelo usuário no LDAP
            conn.search(search_base='DC=digitalup,DC=intranet',
                        search_filter=f'(sAMAccountName={username})',
                        attributes=['cn', 'memberOf', 'homePhone', 'telephoneNumber'])

            if len(conn.entries) > 0:
                user_info = conn.entries[0]
                full_name = user_info.cn.value if hasattr(user_info, 'cn') else None
                is_admin = False

                # Verifica se o usuário pertence ao grupo de Administradores
                if hasattr(user_info, 'memberOf'):
                    for group in user_info.memberOf:
                        if 'CN=Administrators' in group:
                            is_admin = True
                            break

                # Armazena as informações na sessão
                session['logged_in'] = True
                session['username'] = username
                session['full_name'] = full_name
                session['is_admin'] = is_admin  # Salva a informação do grupo Admin

                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"Erro de autenticação LDAP: {e}")
        return False
    finally:
        conn.unbind()

@app.after_request
def add_cache_control_headers(resp):
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate(username, password):
            return redirect(url_for('home'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')

    return render_template('login.html')

# Handle multiple errors
@app.errorhandler(400)
def bad_request_error(e):
    response = jsonify({'message': 'Requisição inválida (400)!'})
    response.status_code = 400
    return response

@app.errorhandler(404)
def not_found_error(e):
    response = jsonify({'message': 'Página não encontrada (404)!'})
    response.status_code = 404
    return response

@app.errorhandler(500)
def internal_error(e):
    response = jsonify({'message': 'Erro interno no servidor (500)!'})
    response.status_code = 500
    return response

@app.errorhandler(429)
def too_many_requests(e):
    response = jsonify({'message': 'Muitas requisições! Por favor, tente novamente mais tarde (429).'})
    response.status_code = 429
    return response

@app.route('/home', methods=['GET'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    full_name = session.get('full_name', 'Usuário')
    username = session.get('username', 'Usuário')
    is_admin = session.get('is_admin', False)  # Pega o status de admin da sessão

    notifications = get_user_notifications(username)
    show_notification = request.args.get('show_notification', 'true') == 'true'

    termo_busca = request.args.get('termo_busca', '')
    estado = request.args.get('estado', '')
    cidade = request.args.get('cidade', '')
    page = int(request.args.get('page', 1))

    estado = remover_acentos(estado)
    cidade = remover_acentos(cidade)

    dados_cnpj = []
    tem_mais_paginas = False
    erro = None
    total_results = 0

    if termo_busca:
        dados_cnpj, total_results, erro = integration.obter_dados_cnpj(termo_busca, estado, cidade, page)
        print(f"Total de resultados encontrados: {total_results}")

        if dados_cnpj:
            for empresa in dados_cnpj:
                cnpj = empresa.get('cnpj')
                detalhes = integration.obter_detalhes_cnpj(cnpj)
                if detalhes:
                    empresa.update(detalhes)

            dados_cnpj.sort(key=lambda empresa: empresa.get('razao_social', '').lower())

            proxima_pagina = integration.obter_dados_cnpj(termo_busca, estado, cidade, page + 1)
            tem_mais_paginas = bool(proxima_pagina)
        else:
            if not erro:
                flash('Nenhum dado encontrado para o termo informado.', 'error')

    if erro:
        flash(erro, 'error')

    return render_template(
        'index.html',
        full_name=full_name,
        notifications=notifications,
        show_notification=show_notification,
        dados_cnpj=dados_cnpj,
        termo_busca=termo_busca,
        estado=estado,
        cidade=cidade,
        page=page,
        tem_mais_paginas=tem_mais_paginas,
        total_results=total_results,
        is_admin=is_admin  # Passa a informação de admin para o template
    )

@app.route('/admin_dashboard')
def admin_dashboard():
    # Pegar os logs de erro
    error_logs = get_error_logs()

    # Renderizar os logs no template
    return render_template('admin_dashboard.html', logs=error_logs)

@app.route('/dismiss_notification', methods=['POST'])
def dismiss_notification():
    if not session.get('logged_in'):
        return jsonify({'error': 'Usuário não autenticado'}), 401

    notification_id = request.form.get('notification_id')
    accepted = request.form.get('accepted') == 'true'

    if notification_id and accepted:
        try:
            # Atualizar o status enviado_bitrix para true
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE "Result"
                SET enviado_bitrix = true
                WHERE id = %s
            """, (notification_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'success': True}), 200
        except Exception as e:
            print(f"Erro ao atualizar notificação: {e}")
            return jsonify({'error': 'Erro ao atualizar notificação'}), 500
    else:
        return jsonify({'error': 'ID de notificação inválido ou ação não especificada'}), 400

@app.route('/enviar', methods=['POST'])
def enviar_varias_empresas():
    empresas = request.get_json()

    for empresa in empresas:
        socio_details = "\n\n".join([
            f"Nome: {socio['nome']}\n"
            f"Qualificação: {socio['qualificacao']}\n"
            f"Faixa Etária: {socio['faixa_etaria']}\n"
            f"Data de Entrada: {socio['data_entrada']}"
            for socio in empresa.get('socios', [])
        ])

        empresa['socios_formatados'] = socio_details if socio_details else 'Nenhum sócio registrado'

    integration.enviar_dados_bitrix(empresas)

    return jsonify({"success": True, "message": "Empresas enviadas com sucesso"})

@app.route('/salvar_csv', methods=['POST'])
def salvar_csv():
    form_data = request.form.to_dict(flat=False)

    empresa = {
        "razao_social": form_data.get('razao_social', [''])[0],
        "nome_fantasia": form_data.get('nome_fantasia', [''])[0],
        "logradouro": form_data.get('logradouro', [''])[0],
        "municipio": form_data.get('municipio', [''])[0],
        "uf": form_data.get('uf', [''])[0],
        "cep": form_data.get('cep', [''])[0],
        "telefone_1": form_data.get('telefone_1', [''])[0],
        "telefone_2": form_data.get('telefone_2', [''])[0],
        "email": form_data.get('email', [''])[0],
        "porte": form_data.get('porte', [''])[0],
        "cnpj": form_data.get('cnpj', [''])[0],
        "socios": [
            {
                "nome": form_data.get('socios_nome[]', [''])[i],
                "faixa_etaria": form_data.get('socios_faixa_etaria[]', [''])[i],
                "qualificacao": form_data.get('socios_qualificacao[]', [''])[i],
                "data_entrada": form_data.get('socios_data_entrada[]', [''])[i]
            }
            for i in range(len(form_data.get('socios_nome[]', [])))
        ]
    }

    file_path = get_user_session_file()

    # Lê os dados do arquivo JSON e adiciona a nova empresa
    with open(file_path, 'r+') as file:
        empresas = json.load(file)
        empresas.append(empresa)
        file.seek(0)
        json.dump(empresas, file)

    return jsonify({'success': True, 'message': 'Empresa adicionada com sucesso.'})

@app.route('/salvar_todas_csv', methods=['POST'])
def salvar_todas_csv():
    form_data = request.get_json()

    empresas = form_data.get('empresas', [])

    file_path = get_user_session_file()

    # Lê os dados existentes no arquivo JSON
    with open(file_path, 'r+') as file:
        empresas_cache = json.load(file)
        empresas_cache.extend(empresas)  # Adiciona as novas empresas
        file.seek(0)
        json.dump(empresas_cache, file)  # Atualiza o arquivo JSON com todas as empresas

    return jsonify({'success': True, 'message': 'Todas as empresas foram salvas com sucesso.'})

from openpyxl.styles import PatternFill, Font, Alignment

@app.route('/baixar_csv')
def baixar_csv():
    file_path = get_user_session_file()

    # Lê os dados do arquivo temporário
    with open(file_path, 'r') as file:
        empresas = json.load(file)

    if not empresas:
        return jsonify({'error': 'Nenhuma empresa disponível para download.'}), 400

    # Criar um arquivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Empresas"

    # Cabeçalhos do XLSX
    headers = [
        'Razão Social', 'Nome Fantasia', 'Logradouro', 'Município', 'UF', 'CEP', 'Telefone 1', 'Telefone 2', 'Email', 'Porte', 'CNPJ'
    ]

    # Adiciona cabeçalhos dinâmicos para os sócios com base no máximo de sócios que alguma empresa tem
    max_socios = max(len(empresa.get('socios', [])) for empresa in empresas) if empresas else 0
    for i in range(1, max_socios + 1):
        headers.extend([f'Sócio {i} Nome', f'Sócio {i} Faixa Etária', f'Sócio {i} Qualificação', f'Sócio {i} Data Entrada'])

    # Adiciona cabeçalhos para os dias da semana
    dias_da_semana = [
        'segunda-feira', 'terça-feira', 'quarta-feira',
        'quinta-feira', 'sexta-feira', 'sábado', 'domingo'
    ]
    headers.extend(dias_da_semana)

    headers.extend([
        'Logradouro Enriquecido', 'Telefone Enriquecido', 'Email Enriquecido', 'Rating', 'Review Count'
    ])

    ws.append(headers)

    # Aplicando estilo e formatação
    contact_group = ['Telefone 1', 'Telefone 2', 'Telefone Enriquecido', 'Email', 'Email Enriquecido']
    address_group = ['Logradouro', 'Município', 'UF', 'CEP', 'Logradouro Enriquecido']
    contact_fill = PatternFill(start_color='FFCCE5', end_color='FFCCE5', fill_type='solid')
    address_fill = PatternFill(start_color='CCFFCC', end_color='CCFFCC', fill_type='solid')
    socio_fill = PatternFill(start_color='CCE5FF', end_color='CCE5FF', fill_type='solid')
    light_gray_fill = PatternFill(start_color='F5F5F5', end_color='F5F5F5', fill_type='solid')
    white_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')

    # Aplicar formatação aos cabeçalhos
    for i, cell in enumerate(ws[1], 1):
        if cell.value in contact_group:
            cell.fill = contact_fill
        elif cell.value in address_group:
            cell.fill = address_fill
        elif 'Sócio' in cell.value:
            cell.fill = socio_fill
        else:
            cell.fill = white_fill
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Monta as queries para o scrap
    queries = [f"{empresa.get('nome_fantasia', empresa.get('razao_social', ''))} {empresa.get('municipio', '')}" for empresa in empresas]

    # Faz o scrap dos dados de forma assíncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scrap_results = loop.run_until_complete(integration.scrap.process_queries(queries))

    # Escreve os dados de cada empresa, incluindo o enriquecimento
    for idx, empresa in enumerate(empresas):
        scrap_data = json.loads(scrap_results[idx]) if scrap_results[idx] else {}

        # Enriquecer os dados da empresa com o scrap
        empresa_enriquecida = integration.atualizar_dados_empresa_com_scrap(empresa.copy(), scrap_data)

        knowledge_graph = scrap_data.get('knowledge_graph', {})
        contact_info = scrap_data.get('consolidated_contact_info', {})

        endereco_enriquecido = contact_info.get('address', knowledge_graph.get('address', ''))
        telefone_enriquecido = contact_info.get('phone', knowledge_graph.get('phone', ''))
        email_enriquecido = contact_info.get('email', '')
        rating = knowledge_graph.get('rating', '')
        review_count = knowledge_graph.get('review_count', '')

        # Processar os horários de funcionamento
        horarios = knowledge_graph.get('hours', {})
        horarios_formatados = [horarios.get(dia, 'Fechado') for dia in dias_da_semana]

        # Prepara os dados dos sócios
        socios_data = []
        for socio in empresa.get('socios', []):
            socios_data.extend([
                socio['nome'],
                socio['faixa_etaria'],
                socio['qualificacao'],
                socio['data_entrada'].replace('\n', ' ')
            ])

        # Adiciona dados dos sócios e preenche com vazios caso não haja sócios
        num_socios = len(empresa.get('socios', []))
        while len(socios_data) < num_socios * 4:
            socios_data.append('')

        # Adiciona os dados na planilha
        ws.append([
            empresa['razao_social'],
            empresa['nome_fantasia'],
            empresa['logradouro'],
            empresa['municipio'],
            empresa['uf'],
            empresa['cep'],
            empresa['telefone_1'],
            empresa['telefone_2'],
            empresa['email'],
            empresa['porte'],
            empresa['cnpj'],
        ] + socios_data + horarios_formatados + [
            endereco_enriquecido,
            telefone_enriquecido,
            email_enriquecido,
            rating,
            review_count
        ])

        # Aplicar formatação nas linhas
        fill = light_gray_fill if idx % 2 == 0 else white_fill
        for cell in ws[idx + 2]:
            cell.fill = fill

    # Ajustar largura das colunas automaticamente
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col) + 2
        ws.column_dimensions[col[0].column_letter].width = max_length

    # Salvar o arquivo em memória
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Remover o arquivo temporário após o download
    os.remove(file_path)
    session.pop('user_id', None)

    # Retorna o XLSX como resposta
    return Response(output,
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment; filename=empresas.xlsx"})

@app.route('/enviar_empresa', methods=['POST'])
def enviar_empresa():
    empresa = {
        "razao_social": request.form.get('razao_social'),
        "nome_fantasia": request.form.get('nome_fantasia'),
        "logradouro": request.form.get('logradouro'),
        "municipio": request.form.get('municipio'),
        "uf": request.form.get('uf'),
        "cep": request.form.get('cep'),
        "telefone_1": request.form.get('telefone_1'),
        "telefone_2": request.form.get('telefone_2'),
        "email": request.form.get('email'),
        "porte": request.form.get('porte'),
        "cnpj": request.form.get('cnpj'),
        "socios": [
            {
                "nome": nome_socio,
                "faixa_etaria": faixa_etaria,
                "qualificacao": qualificacao,
                "data_entrada": data_entrada
            }
            for nome_socio, faixa_etaria, qualificacao, data_entrada in zip(
                request.form.getlist('socios_nome[]'),
                request.form.getlist('socios_faixa_etaria[]'),
                request.form.getlist('socios_qualificacao[]'),
                request.form.getlist('socios_data_entrada[]')
            )
        ]
    }

    usuario_logado = session.get('username', 'Usuário Desconhecido')

    lead_existente = integration.verificar_lead_existente_por_titulo(f"Via Automação - {empresa['razao_social']} - CNPJ: {empresa['cnpj']}")

    if lead_existente:
        lead_id = lead_existente[0]['ID']
        lead_link = f"https://setup.bitrix24.com.br/crm/lead/show/{lead_id}/"
        return jsonify({"success": True, "lead_existente": True, "lead_link": lead_link})
    else:
        # Passar o nome do usuário para a função do integration.py
        integration.enviar_dados_bitrix([empresa], usuario_logado)
        return jsonify({"success": True, "lead_existente": False})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('full_name', None)
    session.pop('phone_number', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)