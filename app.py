from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify, send_file, Response
from ldap3 import Server, Connection, ALL_ATTRIBUTES, SUBTREE
import integration
from notification import get_user_notifications, get_db_connection
import csv
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from io import BytesIO, TextIOWrapper
import uuid
import asyncio
import json
import os
import unicodedata
from unidecode import unidecode
import re
from datetime import datetime
from unidecode import unidecode
from server.errorLog import get_error_logs
from server.loginLog import get_login_logs
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Flask(__name__)
app.secret_key = 'calvo'

def remover_acentos(texto):
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

def ajustar_largura_colunas(ws):
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Pega a letra da coluna
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = (max_length + 2)  # Ajuste com base no tamanho do texto
        ws.column_dimensions[column].width = adjusted_width

def gerar_excel(empresas, scrap_results):
    # Criar uma nova pasta de trabalho e uma planilha
    wb = Workbook()
    ws = wb.active
    ws.title = "Empresas"

    # Cabeçalhos das colunas principais
    headers = [
        "Razão Social", "Nome Fantasia", "CNPJ", "Endereço",
        "Telefone 1", "Telefone 2", "E-mail", "Telefone Enriquecido"
    ]

    # Encontrar o número máximo de sócios para adicionar as colunas de forma dinâmica
    max_socios = max(len(empresa['socios']) for empresa in empresas)

    # Cabeçalhos dinâmicos para sócios
    for i in range(1, max_socios + 1):
        headers.extend([f"Nome Sócio {i}", f"Faixa Etária Sócio {i}", f"Qualificação Sócio {i}", f"Data Entrada Sócio {i}"])

    # Adicionar os cabeçalhos à planilha
    ws.append(headers)

    # Estilo para os cabeçalhos
    header_fill = PatternFill(start_color="15294b", end_color="15294b", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    # Aplicar estilos aos cabeçalhos
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Estilo para contorno e bordas internas
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Iterar pelas empresas e scrap_results ao mesmo tempo
    for empresa, enriched_data_str in zip(empresas, scrap_results):
        # Converta a string JSON para dicionário
        try:
            enriched_data = json.loads(enriched_data_str)  # Tente carregar o JSON
        except json.JSONDecodeError:
            enriched_data = {}  # Se falhar, use um dicionário vazio

        # Dados principais da empresa
        row = [
            empresa['razao_social'],
            empresa['nome_fantasia'],
            empresa['cnpj'],
            empresa['logradouro'],
            empresa['telefone_1'],
            empresa['telefone_2'],
            empresa['email'],
            enriched_data.get('consolidated_contact_info', {}).get('phone', '')  # Telefone do enriched_info
        ]

        # Adicionar as informações dos sócios (ou deixar em branco se não houver dados)
        for socio in empresa['socios']:
            row.extend([
                socio.get('nome', ''),  # Deixa vazio se não houver valor
                socio.get('faixa_etaria', ''),
                socio.get('qualificacao', ''),
                socio.get('data_entrada', '')
            ])

        # Preenche células vazias para sócios que não existem
        socios_faltantes = max_socios - len(empresa['socios'])
        if socios_faltantes > 0:
            row.extend([''] * 4 * socios_faltantes)  # Preenche com células vazias

        # Adicionar a linha completa na planilha
        ws.append(row)

    # Ajustar a largura das colunas com base no conteúdo
    ajustar_largura_colunas(ws)

    # Aplicar bordas nas células dentro da tabela
    for row in ws.iter_rows(min_row=2, max_col=len(headers), max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

    # Remover bordas fora da tabela
    for row in ws.iter_rows(min_row=ws.max_row+1, max_col=len(headers)):
        for cell in row:
            cell.border = Border()  # Sem borda

    # Salvar em um objeto BytesIO e retornar
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def carregar_blacklist():
    blacklist = {}
    try:
        with open('resource/blacklist.csv', 'r', newline='') as blacklist_file:
            reader = csv.DictReader(blacklist_file)
            for row in reader:
                cnpj = row['cnpj']
                user = row['user']
                datetime_str = row['datetime']
                blacklist[cnpj] = {
                    'user': user,
                    'datetime': datetime_str
                }
    except FileNotFoundError:
        print("O arquivo blacklist.csv não foi encontrado.")
    return blacklist

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

@app.template_filter('format_cnpj')
def format_cnpj(cnpj):
    if cnpj and len(cnpj) == 14:  # Verifica se o CNPJ tem 14 dígitos
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

@app.template_filter('format_datetime')
def format_datetime(dt_str):
    if dt_str:
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M h")
        except ValueError:
            return dt_str
    return ""

@app.template_filter('formata_real')
def formata_real(valor):
    try:
        valor_float = float(valor) if isinstance(valor, str) else valor
        return locale.currency(valor_float, grouping=True, symbol="R$")
    except (TypeError, ValueError):
        return "R$0,00"

@app.template_filter('capitalize')
def capitalize(value):
    if value.isupper() and len(value) == 2:  # Manter UF em maiúsculas
        return value
    else:
        return value.capitalize()

@app.template_filter('format_cep')
def format_cep(value):
    if value and len(value) == 8 and value.isdigit():
        return f"{value[:5]}-{value[5:]}"
    return value

@app.template_filter('format_phone')
def format_phone(value):
    if value and value.isdigit():
        if len(value) == 10:
            ddd = value[:2]
            prefixo = value[2:6]
            sufixo = value[6:]
            if prefixo[0] in '6 7 8 9':
                return f"({ddd}) 9{prefixo}-{sufixo}"
            return f"({ddd}) {prefixo}-{sufixo}"
        elif len(value) == 11:
            ddd = value[:2]
            prefixo = value[2:7]
            sufixo = value[7:]
            return f"({ddd}) {prefixo}-{sufixo}"
    return value

@app.route('/home', methods=['GET'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    full_name = session.get('full_name', 'Usuário')
    username = session.get('username', 'Usuário')
    is_admin = session.get('is_admin', False)

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

    # Carregar dados da blacklist
    blacklist = carregar_blacklist()

    if termo_busca:
        dados_cnpj, total_results, erro = integration.obter_dados_cnpj(termo_busca, estado, cidade, page)
        print(f"Total de resultados encontrados: {total_results}")

        if dados_cnpj:
            for empresa in dados_cnpj:
                cnpj = empresa.get('cnpj')
                detalhes = integration.obter_detalhes_cnpj(cnpj)
                if detalhes:
                    # Atualizar o dicionário empresa com os detalhes, incluindo capital social
                    empresa.update(detalhes)

                # Adicionar informações da blacklist, se existir
                if cnpj in blacklist:
                    empresa['blacklist_info'] = blacklist[cnpj]

            # Ordenar pelo nome da razão social
            dados_cnpj.sort(key=lambda empresa: empresa.get('razao_social', '').lower())

            # Verificar se existe próxima página de resultados
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
        is_admin=is_admin
    )


@app.route('/admin_dashboard')
def admin_dashboard():
    # Verificar se o usuário está logado e se é administrador
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Acesso negado. Você não tem permissão para acessar essa página.', 'error')
        return redirect(url_for('home'))

    # Pegar os logs de erro
    error_logs = get_error_logs()

    # Renderizar os logs no template
    return render_template('admin_dashboard.html', logs=error_logs)

@app.route('/error_log')
def error_log():
    # Verificar se o usuário está logado e se é administrador
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Acesso negado. Você não tem permissão para acessar essa página.', 'error')
        return redirect(url_for('home'))

    # Pegar os logs de erro
    error_logs = get_error_logs()

    # Renderizar os logs no template
    return render_template('error_log.html', logs=error_logs)

@app.route('/login_log')
def login_log():
    # Verificar se o usuário está logado e se é administrador
    if not session.get('logged_in') or not session.get('is_admin'):
        flash('Acesso negado. Você não tem permissão para acessar essa página.', 'error')
        return redirect(url_for('home'))

    # Pegar os logs de login
    login_logs = get_login_logs()

    # Renderizar os logs no template
    return render_template('login_log.html', logs=login_logs)

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

def normalizar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

@app.route('/salvar_todas_csv', methods=['POST'])
def salvar_todas_csv():
    form_data = request.get_json()
    empresas = form_data.get('empresas', [])
    file_path = get_user_session_file()

    # Lê os CNPJs da blacklist
    blacklist_cnpjs = set()
    try:
        with open('resource/blacklist.csv', mode='r') as blacklist_file:
            csv_reader = csv.DictReader(blacklist_file)
            for row in csv_reader:
                cnpj_blacklist = normalizar_cnpj(row['cnpj'].strip())
                blacklist_cnpjs.add(cnpj_blacklist)
    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'Arquivo de blacklist não encontrado.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    # Debug: imprime CNPJs da blacklist
    print("CNPJs na blacklist:", blacklist_cnpjs)

    # Lê os dados existentes no arquivo JSON
    try:
        with open(file_path, 'r+') as file:
            try:
                empresas_cache = json.load(file)
            except json.JSONDecodeError:
                empresas_cache = []

            for empresa in empresas:
                cnpj = empresa.get('cnpj')
                cnpj_normalizado = normalizar_cnpj(cnpj)

                if cnpj_normalizado and cnpj_normalizado not in blacklist_cnpjs:
                    # Remove os acentos dos campos de cada empresa e sócios
                    empresa['razao_social'] = unidecode(empresa['razao_social'])
                    empresa['nome_fantasia'] = unidecode(empresa['nome_fantasia'])
                    empresa['logradouro'] = unidecode(empresa['logradouro'])
                    empresa['municipio'] = unidecode(empresa['municipio'])
                    empresa['porte'] = unidecode(empresa['porte'])

                    # Remover acentos dos sócios
                    for socio in empresa['socios']:
                        socio['nome'] = unidecode(socio['nome'])
                        socio['faixa_etaria'] = unidecode(socio['faixa_etaria'])
                        socio['qualificacao'] = unidecode(socio['qualificacao'])
                        socio['data_entrada'] = unidecode(socio['data_entrada'])

                    empresas_cache.append(empresa)
                else:
                    print("Ignorando CNPJ (Já processado):", cnpj_normalizado)

            file.seek(0)
            json.dump(empresas_cache, file, indent=4)
            file.truncate()

    except FileNotFoundError:
        return jsonify({'success': False, 'message': 'Arquivo de cache não encontrado.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    return jsonify({'success': True, 'message': 'Todas as empresas, novas, foram salvas com sucesso.'})

@app.route('/baixar_csv')
def baixar_csv():
    file_path = get_user_session_file()

    # Lê os dados do arquivo temporário
    with open(file_path, 'r') as file:
        empresas = json.load(file)

    if not empresas:
        return jsonify({'error': 'Nenhuma empresa disponível para download.'}), 400

    # Faz o scrap dos dados de forma assíncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    queries = [f"{empresa.get('nome_fantasia', empresa.get('razao_social', ''))} {empresa.get('municipio', '')}" for empresa in empresas]
    scrap_results = loop.run_until_complete(integration.scrap.process_queries(queries))

    # Blacklist
    blacklist_path = 'resource/blacklist.csv'

    # Verifica se o arquivo já existe, senão cria com cabeçalhos
    if not os.path.exists(blacklist_path):
        with open(blacklist_path, 'w', newline='') as blacklist_file:
            writer = csv.writer(blacklist_file)
            writer.writerow(['cnpj', 'user', 'datetime'])  # Adiciona cabeçalhos

    # Nome do usuário logado e data/hora atual
    username = session.get('username', 'Usuário desconhecido')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Adiciona os CNPJs no CSV de blacklist
    with open(blacklist_path, 'a', newline='') as blacklist_file:
        writer = csv.writer(blacklist_file)
        for empresa in empresas:
            cnpj_normalizado = normalizar_cnpj(empresa['cnpj'])  # Normaliza o CNPJ
            writer.writerow([cnpj_normalizado, username, current_time])

    # Chama a função para gerar o Excel
    output = gerar_excel(empresas, scrap_results)

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