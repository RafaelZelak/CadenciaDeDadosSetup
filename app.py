from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from ldap3 import Server, Connection, ALL_ATTRIBUTES, SUBTREE
import integration

app = Flask(__name__)
app.secret_key = 'calvo'

def authenticate(username, password):
    domain = 'digitalup.intranet'
    server = Server(domain, get_info=ALL_ATTRIBUTES)
    user = f'{username}@{domain}'
    conn = Connection(server, user=user, password=password)

    try:
        if conn.bind():
            conn.search(search_base='DC=digitalup,DC=intranet',
                        search_filter=f'(sAMAccountName={username})',
                        attributes=['cn', 'homePhone', 'telephoneNumber'])

            if len(conn.entries) > 0:
                user_info = conn.entries[0]

                print(user_info)

                full_name = user_info.cn.value if hasattr(user_info, 'cn') else None

                session['logged_in'] = True
                session['username'] = username
                session['full_name'] = full_name

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

@app.route('/home', methods=['GET'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    full_name = session.get('full_name', 'Usuário')

    # Pegar os parâmetros da URL (GET)
    termo_busca = request.args.get('termo_busca', '')
    page = int(request.args.get('page', 1))  # Pegar a página da URL, por padrão a 1

    dados_cnpj = []
    if termo_busca:
        dados_cnpj = integration.obter_dados_cnpj(termo_busca, page)
        if dados_cnpj:
            # Obter detalhes enriquecidos para cada CNPJ
            for empresa in dados_cnpj:
                cnpj = empresa.get('cnpj')
                detalhes = integration.obter_detalhes_cnpj(cnpj)
                if detalhes:
                    empresa.update(detalhes)
        else:
            flash('Nenhum dado encontrado para o termo informado.', 'error')

    return render_template('index.html', full_name=full_name, dados_cnpj=dados_cnpj, termo_busca=termo_busca, page=page)
@app.route('/enviar', methods=['POST'])
def enviar_varias_empresas():
    # Receber os dados de várias empresas
    empresas = request.get_json()

    # Enviar os dados dessas empresas para o Bitrix24
    integration.enviar_dados_bitrix(empresas)

    return jsonify({"success": True, "message": "Empresas enviadas com sucesso"})
@app.route('/enviar_empresa', methods=['POST'])
def enviar_empresa():
    # Obter os dados da empresa
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

    # Enviar os dados dessa empresa específica para o Bitrix24
    integration.enviar_dados_bitrix([empresa])

    return jsonify({"success": True, "message": "Empresa enviada com sucesso"})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('full_name', None)
    session.pop('phone_number', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)