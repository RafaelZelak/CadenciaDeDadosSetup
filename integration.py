import cloudscraper
import requests
import re
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import scrap
import json
import asyncio


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

def filtrar_cnpjs_por_palavras_chave(cnpjs, palavras_chave):
    palavras_chave_lower = [palavra.lower() for palavra in palavras_chave]
    return [
        cnpj for cnpj in cnpjs
        if any(palavra in cnpj.get('razao_social', '').lower() for palavra in palavras_chave_lower)
    ]

# Exemplo de uso:
palavras_chave = ["conta", "contabil", "contabilidade", "advo", "advogado", "advocacia", "associ", "associação"]
termo = "conta"  # Termo inicial para a busca
cnpjs = obter_dados_cnpj(termo)
if cnpjs:
    cnpjs_filtrados = filtrar_cnpjs_por_palavras_chave(cnpjs, palavras_chave)

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

def enviar_dados_bitrix(empresas):
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
            socio_details = "\n\n".join([f"Nome: {socio['nome']}\n"
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
            if empresa.get('telefone_1'):
                telefones.append({"VALUE": empresa.get('telefone_1', ''), "VALUE_TYPE": "WORK"})
            if empresa.get('telefone_2'):
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
