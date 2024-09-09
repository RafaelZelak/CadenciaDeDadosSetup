import cloudscraper
import requests

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

    response = scraper.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('data', {}).get('cnpj', [])
    else:
        print(f"Erro: {response.status_code}, {response.text}")
        return None

# Função para obter os dados enriquecidos do CNPJ via BrasilAPI
def obter_detalhes_cnpj(cnpj):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        socios = [
            {
                "nome": socio.get("nome_socio", ""),
                "faixa_etaria": socio.get("faixa_etaria", ""),
                "qualificacao": socio.get("qualificacao_socio", ""),
                "data_entrada": socio.get("data_entrada_sociedade", "")
            }
            for socio in dados.get("qsa", [])
            if socio.get("nome_socio")  # Garante que sócios válidos sejam incluídos
        ]

        # Retorna dados com verificação para evitar None
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
    else:
        print(f"Erro ao buscar detalhes do CNPJ: {response.status_code}, {response.text}")
        return {}

# Função para enviar os dados ao CRM do Bitrix24
def enviar_dados_bitrix(empresas):
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.lead.add.json"
    for empresa in empresas:
        # Formatando detalhes dos sócios com mais espaçamento
        socio_details = "\n\n".join([
            f"Nome: {socio['nome']}\n"
            f"Qualificação: {socio['qualificacao']}\n"
            f"Faixa Etária: {socio['faixa_etaria']}\n"
            f"Data de Entrada: {socio['data_entrada']}"
            for socio in empresa.get('socios', [])
        ])

        # Formatando o endereço
        logradouro = empresa.get('logradouro', '')
        municipio = empresa.get('municipio', '')
        uf = empresa.get('uf', '')
        cep = empresa.get('cep', '')

        # Padronizando o endereço no formato desejado
        endereco_padronizado = f"{logradouro} - {municipio} {uf} - {cep[:5]}-{cep[5:]}"

        # Filtra telefones válidos
        telefones = []
        if empresa.get('telefone_1'):
            telefones.append({"VALUE": empresa.get('telefone_1', ''), "VALUE_TYPE": "WORK"})
        if empresa.get('telefone_2'):
            telefones.append({"VALUE": empresa.get('telefone_2', ''), "VALUE_TYPE": "WORK"})

        payload = {
            "fields": {
                "TITLE": f"Via Automação - {empresa.get('razao_social', '')}",
                "NAME": empresa.get('nome_fantasia', ''),
                "STATUS_ID": "NEW",
                "CURRENCY_ID": "BRL",
                "OPPORTUNITY": "0",
                "ADDRESS": endereco_padronizado,  # Usando endereço padronizado
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

        response = requests.post(bitrix_url, json=payload)
        if response.status_code == 200:
            print(f"Lead criado com sucesso: {response.json()}")
        else:
            print(f"Erro ao criar lead: {response.status_code}, {response.text}")
