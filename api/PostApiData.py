import requests
import json

def criar_negocio(razao_social, nome_fantasia, cnpj, endereco, telefone1, telefone2, telefone3, email, capital_social, socios, scrap_data):

    # Converte o scrap_data de string para dicionário JSON
    try:
        scrap_data = json.loads(scrap_data)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar scrap_data: {e}")
        scrap_data = {}

    # Extrai dados do scrap_results (scrap_data)
    telefone_scrap = scrap_data.get('consolidated_contact_info', {}).get('phone', '')
    endereco_scrap = scrap_data.get('consolidated_contact_info', {}).get('address', '')
    email_scrap = scrap_data.get('consolidated_contact_info', {}).get('email', '')

    # Garantir que o telefone seja preenchido corretamente
    telefone1 = telefone1 or telefone_scrap
    telefone2 = telefone2 or ''
    telefone3 = telefone3 or ''

    # Formatar os sócios
    socios_list = socios or []
    socios_formatados = ' | '.join([f"Socio {i+1}: {socio['nome']}, {socio['qualificacao']}" for i, socio in enumerate(socios_list)])

    # Dados do novo negócio
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.deal.add"
    dados_negocio = {
        "fields": {
            "TITLE": f"Via Automação - {razao_social} - CNPJ: {cnpj}",
            "UF_CRM_1729682188409": razao_social,    # Razão Social
            "UF_CRM_1729682198513": nome_fantasia,   # Nome Fantasia
            "UF_CRM_1729682208297": cnpj,            # CNPJ
            "UF_CRM_1729682242372": endereco or endereco_scrap,  # Endereço
            "UF_CRM_1729682256245": telefone1,       # Telefone 1
            "UF_CRM_1729684520107": telefone2,       # Telefone 2
            "UF_CRM_1729684527227": telefone3,       # Telefone 3
            "UF_CRM_1729684539443": email or email_scrap,  # E-mail
            "UF_CRM_1729684551068": capital_social,  # Capital Social
            "UF_CRM_1729684638352": socios_formatados  # Sócios formatados
        }
    }

    # Fazer a requisição POST para criar o novo negócio no Bitrix24
    response = requests.post(bitrix_url, json=dados_negocio)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        resultado = response.json()
        print(f"Negócio criado com sucesso! ID: {resultado['result']}")
    else:
        print(f"Erro ao criar negócio: {response.status_code}")
