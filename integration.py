import cloudscraper
import requests
import re
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

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

    # Verifica se o nome fantasia está presente
    if not empresa.get('nome_fantasia', '').strip():
        erros.append("Nome fantasia da empresa está ausente.")

    # Verifica se pelo menos um telefone ou e-mail está presente
    if not (empresa.get('telefone_1') or empresa.get('telefone_2') or empresa.get('email')):
        erros.append("É necessário pelo menos um telefone ou e-mail de contato.")

    return erros

# Função para obter os dados do CNPJ na Casa dos Dados
def obter_dados_cnpj(termo, estado='', cidade='', page=1):
    scraper = cloudscraper.create_scraper()
    url = "https://api.casadosdados.com.br/v2/public/cnpj/search"
    data = {
        "query": {
            "termo": [termo],
            "uf": [estado] if estado else [],
            "municipio": [cidade] if cidade else [],
            "situacao_cadastral": "ATIVA"
        },
        "extras": {
            "excluir_mei": True,
            "com_email": True,
            "com_contato_telefonico": True,
            "somente_fixo": False,
            "somente_celular": False,
            "somente_matriz": True
        },
        "page": page
    }

    try:
        response = scraper.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {}).get('cnpj', [])
    except (ConnectionError, Timeout):
        print("Erro de conexão ou tempo de resposta excedido ao obter dados do CNPJ.")
        return None
    except HTTPError as e:
        print(f"Erro HTTP ao tentar obter dados do CNPJ: {e}")
        return None
    except RequestException as e:
        print(f"Erro inesperado na requisição ao obter dados do CNPJ: {e}")
        return None

# Função para obter os dados enriquecidos do CNPJ via BrasilAPI
def obter_detalhes_cnpj(cnpj):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        response = requests.get(url, timeout=10)
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
            "razao_social": dados.get("razao_social", "")
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

# Função para enviar leads ao Bitrix, com validação de dados
def enviar_dados_bitrix(empresas):
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.lead.add.json"
    for empresa in empresas:
        # Validação dos dados da empresa
        erros = validar_dados_empresa(empresa)
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
            socio_details = "\n\n".join([
                f"Nome: {socio['nome']}\n"
                f"Qualificação: {socio['qualificacao']}\n"
                f"Faixa Etária: {socio['faixa_etaria']}\n"
                f"Data de Entrada: {socio['data_entrada']}"
                for socio in empresa.get('socios', [])
            ])

            logradouro = empresa.get('logradouro', '')
            municipio = empresa.get('municipio', '')
            uf = empresa.get('uf', '')
            cep = empresa.get('cep', '')

            endereco_padronizado = f"{logradouro} - {municipio} {uf} - {cep[:5]}-{cep[5:]}"

            telefones = []
            if empresa.get('telefone_1'):
                telefones.append({"VALUE": empresa.get('telefone_1', ''), "VALUE_TYPE": "WORK"})
            if empresa.get('telefone_2'):
                telefones.append({"VALUE": empresa.get('telefone_2', ''), "VALUE_TYPE": "WORK"})

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
                    "COMMENTS": (
                        f"Porte: {empresa.get('porte', '')}\n\n"
                        f"Sócios:\n\n{socio_details}"
                    )
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

