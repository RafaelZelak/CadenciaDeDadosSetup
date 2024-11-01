import cloudscraper
import requests
import re
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import scrap
import json
import asyncio
import csv
import os
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer("portuguese")

def expandir_termo(termo):
    radical = stemmer.stem(termo)

    # Possíveis sufixos comuns no português
    sufixos = ['a', 'aria', 'idade', 'mento', 'ção', 'dor', 'ismo', 'ista', 'oso', 'ável', 'ção', 'eria', 'ório', 'teria']

    expansoes = [termo] + [radical + sufixo for sufixo in sufixos]

    return expansoes

# Função auxiliar para validar o CNPJ
def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)  # Remove qualquer caractere que não seja número
    if len(cnpj) != 14:
        return False
    # Adicione mais validações de CNPJ se necessário (como o cálculo dos dígitos verificadores)
    return True

# Função auxiliar para validar se os dados essenciais estão presentes
def validar_dados_empresa(empresa):
    erros = []

    # Verifica se o CNPJ está presente e é válido
    cnpj = empresa.get('cnpj', '')
    if not cnpj:
        erros.append("CNPJ está ausente.")
    elif not validar_cnpj(cnpj):
        erros.append(f"CNPJ inválido: {cnpj}")

    # Verifica se a razão social está presente
    if not empresa.get('razao_social', '').strip():
        erros.append("Razão social da empresa está ausente.")

    # Verifica se pelo menos um telefone ou e-mail está presente
    if not (empresa.get('telefone_1') or empresa.get('telefone_2') or empresa.get('email')):
        erros.append("É necessário pelo menos um telefone ou e-mail de contato.")

    return erros

# Função para obter os dados do CNPJ na Casa dos Dados
def obter_dados_cnpj(termo, estado='', cidade='',bairro='', page=1):
    scraper = cloudscraper.create_scraper()
    url = "https://api.casadosdados.com.br/v2/public/cnpj/search"
    print(f"Bairro:{bairro}")
    # Expande o termo para incluir possíveis variações
    termos_expandidos = expandir_termo(termo)
    data = {
        "query": {
            "termo": termos_expandidos,
            "uf": [estado] if estado else [],
            "municipio": [cidade] if cidade else [],
            "bairro": [bairro] if bairro else [],
            "situacao_cadastral": "ATIVA"
        },
        "extras": {
            "excluir_mei": True,
            "com_email": False,
            "com_contato_telefonico": True,
            "somente_fixo": False,
            "somente_celular": False,
            "somente_matriz": False
        },
        "page": page
    }

    try:
        response = scraper.post(url, json=data, timeout=10)
        response.raise_for_status()

        # Obter o total de resultados
        total_results = response.json().get('data', {}).get('count', 0)
        dados_cnpj = response.json().get('data', {}).get('cnpj', [])

        # Ordenar as empresas pelo CNPJ ou razão social (ordenação constante)
        dados_cnpj.sort(key=lambda empresa: empresa.get('cnpj', ''))

        return dados_cnpj, total_results, None

    except (ConnectionError, Timeout):
        print("Erro de conexão ou tempo de resposta excedido ao obter dados do CNPJ.")
        return None, 0, "Erro de conexão ou tempo de resposta excedido."
    except HTTPError as e:
        if e.response.status_code == 429:
            print("Erro HTTP 429: Too Many Requests.")
            return None, 0, "Você atingiu o limite de requisições. Tente novamente mais tarde."
        print(f"Erro HTTP ao tentar obter dados do CNPJ: {e}")
        return None, 0, f"Erro HTTP: {e}"
    except RequestException as e:
        print(f"Erro inesperado na requisição ao obter dados do CNPJ: {e}")
        return None, 0, f"Erro inesperado: {e}"


# Função para obter os dados enriquecidos do CNPJ via BrasilAPI
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import random

def obter_detalhes_cnpj(cnpj):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
            "Mozilla/5.0 (Linux; U; Android 11; en-us; SM-N986U Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36"
        ]),
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        dados = response.json()
        socios = [
            {
                "nome": socio.get("nome_socio", ""),
                "faixa_etaria": socio.get("faixa_etaria", ""),
                "qualificacao": socio.get("qualificacao_socio", ""),
                "data_entrada": socio.get("data_entrada_sociedade", "")
            }
            for socio in dados.get("qsa", [])
            if socio.get("nome_socio")
        ]

        return {
            "email": dados.get("email", ""),
            "telefone_1": dados.get("ddd_telefone_1", ""),
            "telefone_2": dados.get("ddd_telefone_2", ""),
            "porte": dados.get("porte", ""),
            "socios": socios,
            "logradouro": dados.get("logradouro", ""),
            "municipio": dados.get("municipio", ""),
            "uf": dados.get("uf", ""),
            "cep": dados.get("cep", ""),
            "nome_fantasia": dados.get("nome_fantasia", ""),
            "razao_social": dados.get("razao_social", ""),
            "capital_social": dados.get("capital_social", ""),
            "numero": dados.get("numero", ""),
            "bairro": dados.get("bairro", "")
        }
    except (ConnectionError, Timeout):
        print("Erro de conexão ou tempo de resposta excedido ao obter detalhes do CNPJ.")
        return {}
    except HTTPError as e:
        print(f"Erro HTTP ao tentar obter detalhes do CNPJ: {e}")
        return {}
    except RequestException as e:
        print(f"Erro inesperado na requisição ao obter detalhes do CNPJ: {e}")
        return {}

# Função para verificar se um lead já existe no Bitrix pelo título
def verificar_lead_existente_por_titulo(titulo):
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.lead.list.json"
    filtros = {
        "filter": {
            "TITLE": titulo
        },
        "select": ["ID", "TITLE", "STATUS_ID"]
    }

    try:
        response = requests.post(bitrix_url, json=filtros, timeout=10)
        response.raise_for_status()

        leads = response.json().get('result', [])
        return leads if leads else None
    except (ConnectionError, Timeout):
        print("Erro de conexão ou tempo de resposta excedido ao verificar lead no Bitrix.")
        return None
    except HTTPError as e:
        print(f"Erro HTTP ao tentar verificar lead no Bitrix: {e}")
        return None
    except RequestException as e:
        print(f"Erro inesperado na requisição ao verificar lead no Bitrix: {e}")
        return None

def salvar_dados_fracos_csv(empresa, usuario_logado):
    caminho_arquivo = 'data/dados_fracos.csv'

    if not os.path.exists('data'):
        os.makedirs('data')

    with open(caminho_arquivo, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if file.tell() == 0:
            writer.writerow(['Nome Fantasia / Razão Social', 'Município', 'Usuário'])

        nome_fantasia_ou_razao_social = empresa.get('nome_fantasia', empresa.get('razao_social', ''))
        municipio = empresa.get('municipio', '')

        writer.writerow([nome_fantasia_ou_razao_social, municipio, usuario_logado])

    print(f"Dados fracos salvos no CSV: {nome_fantasia_ou_razao_social}, {municipio}, Usuário: {usuario_logado}")

def enviar_dados_bitrix(empresas, usuario_logado):
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.lead.add.json"

    # Lista de queries a ser enviada para o scrap.py
    queries = [f"{empresa.get('nome_fantasia', empresa.get('razao_social', ''))} {empresa.get('municipio', '')}" for empresa in empresas]

    # Chama a função de scrap e aguarda o resultado de forma síncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scrap_results = loop.run_until_complete(scrap.process_queries(queries))

    for idx, empresa in enumerate(empresas):
        # Atualiza os dados da empresa com o resultado do scrap
        if scrap_results[idx]:
            scrap_data = json.loads(scrap_results[idx])
            empresa = atualizar_dados_empresa_com_scrap(empresa, scrap_data)

        # Validação dos dados da empresa
        erros = validar_dados_empresa(empresa)

        # Verifica se os telefones são placeholders ou estão ausentes
        placeholder_telefone = '+555525501001'
        telefone_1 = empresa.get('telefone_1')
        telefone_2 = empresa.get('telefone_2')

        if (telefone_1 == placeholder_telefone or not telefone_1) and (telefone_2 == placeholder_telefone or not telefone_2):
            # Dados fracos (sem telefone válido)
            salvar_dados_fracos_csv(empresa, usuario_logado)
            continue  # Pula para a próxima empresa

        if erros:
            print(f"Erros encontrados na empresa {empresa.get('razao_social', 'Desconhecida')} - CNPJ: {empresa.get('cnpj', 'Desconhecido')}")
            for erro in erros:
                print(f"Erro: {erro}")
            continue  # Não tenta enviar dados ao Bitrix se houver erros

        cnpj = empresa.get('cnpj', 'Desconhecido')
        titulo = f"Via Automação - {empresa.get('razao_social', '')} - CNPJ: {cnpj}"

        lead_existente = verificar_lead_existente_por_titulo(titulo)

        if lead_existente:
            lead_id = lead_existente[0]['ID']
            lead_link = f"https://setup.bitrix24.com.br/crm/lead/show/{lead_id}/"
            print(f"Lead já existe: {lead_id}, {lead_existente[0]['TITLE']}. Acesse o lead aqui: {lead_link}")
            continue
        else:
            # Montagem dos detalhes dos sócios
            socio_details = "\n\n".join([f"Nome: {', '.join(socio['nome']) if isinstance(socio['nome'], list) else socio['nome']}\n"
                                         f"Qualificação: {socio['qualificacao']}\n"
                                         f"Faixa Etária: {socio['faixa_etaria']}\n"
                                         f"Data de Entrada: {socio['data_entrada']}"
                                         for socio in empresa.get('socios', [])])

            logradouro = empresa.get('logradouro', '')
            municipio = empresa.get('municipio', '')
            uf = empresa.get('uf', '')
            cep = empresa.get('cep', '')

            endereco_padronizado = f"{logradouro} - {municipio} {uf} - {cep[:5]}-{cep[5:]}"

            telefones = []
            if empresa.get('telefone_1') and empresa.get('telefone_1') != placeholder_telefone:
                telefones.append({"VALUE": empresa.get('telefone_1', ''), "VALUE_TYPE": "WORK"})
            if empresa.get('telefone_2') and empresa.get('telefone_2') != placeholder_telefone:
                telefones.append({"VALUE": empresa.get('telefone_2', ''), "VALUE_TYPE": "WORK"})

            # Formatação do campo de comentários com os dados enriquecidos e sócios
            comentarios = (
                f"Nome: {scrap_data.get('knowledge_graph', {}).get('title', 'Não disponível')}\n"
                f"Rating: {scrap_data.get('knowledge_graph', {}).get('rating', 'Não disponível')} ({scrap_data.get('knowledge_graph', {}).get('review_count', 'Não disponível')})\n"
                f"Endereço: {scrap_data.get('knowledge_graph', {}).get('address', 'Não disponível')}\n"
                f"Telefone: {scrap_data.get('consolidated_contact_info', {}).get('phone', 'Não disponível')}\n"
                f"Email: {scrap_data.get('consolidated_contact_info', {}).get('email', 'Não disponível')}\n\n"
                f"Redes Sociais: {', '.join(scrap_data.get('consolidated_contact_info', {}).get('social_media_profiles', [])) or 'Não disponível'}\n\n"
                f"Horários de Funcionamento:\n" +
                "\n".join([f"{dia}: {horario}" for dia, horario in scrap_data.get('knowledge_graph', {}).get('hours', {}).items()]) +
                f"\n\nSócios:\n\n{socio_details}\n"
            )

            payload = {
                "fields": {
                    "TITLE": titulo,
                    "NAME": empresa.get('nome_fantasia', ''),
                    "STATUS_ID": "NEW",
                    "CURRENCY_ID": "BRL",
                    "OPPORTUNITY": "0",
                    "ADDRESS": endereco_padronizado,
                    "ADDRESS_CITY": municipio,
                    "ADDRESS_REGION": uf,
                    "ADDRESS_POSTAL_CODE": cep,
                    "UF": uf,
                    "PHONE": telefones,
                    "EMAIL": [{"VALUE": empresa.get('email', ''), "VALUE_TYPE": "WORK"}],
                    "COMMENTS": comentarios
                },
                "params": {"REGISTER_SONET_EVENT": "Y"}
            }

            try:
                response = requests.post(bitrix_url, json=payload, timeout=10)
                response.raise_for_status()
                print(f"Lead criado com sucesso: {response.json()}")

            except (ConnectionError, Timeout):
                print("Erro de conexão ou tempo de resposta excedido ao criar lead no Bitrix.")
            except HTTPError as e:
                print(f"Erro HTTP ao tentar criar lead no Bitrix: {e}")
            except RequestException as e:
                print(f"Erro inesperado na requisição ao Bitrix: {e}")

def atualizar_dados_empresa_com_scrap(empresa, scrap_data):
    """Atualiza os dados da empresa com as informações obtidas via scrap."""
    contact_info = scrap_data.get('consolidated_contact_info', {})
    knowledge_graph = scrap_data.get('knowledge_graph', {})

    # Atualizar telefone, email e endereço se disponíveis no scrap
    empresa['telefone_1'] = contact_info.get('phone', empresa.get('telefone_1', ''))
    empresa['email'] = contact_info.get('email', empresa.get('email', ''))
    empresa['logradouro'] = contact_info.get('address', empresa.get('logradouro', ''))

    return empresa
