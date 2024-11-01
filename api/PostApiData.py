import requests

def criar_negocio(razao_social, nome_fantasia, cnpj, endereco, telefone1, telefone2, telefone3, email, capital_social, socios, scrap_data, social_media_profiles, website):
    # Extrai dados do scrap_results diretamente do dicionário scrap_data
    telefone_scrap = scrap_data.get('consolidated_contact_info', {}).get('phone', '')
    # Ajuste para pegar o endereço de 'address_maps' caso 'address' esteja vazio
    endereco_scrap = scrap_data.get('address') or scrap_data.get('address_maps', '')
    email_scrap = scrap_data.get('email', '')

    # Garantir que o telefone seja preenchido corretamente
    telefone1 = telefone1 or telefone_scrap
    telefone2 = telefone2 or scrap_data.get('phone2', '')
    telefone3 = telefone3 or ''

    # Formatar os sócios
    socios_list = socios or []
    socios_formatados = ' | '.join([f"Socio {i+1}: {socio['nome']}, {socio['qualificacao']}" for i, socio in enumerate(socios_list)])

    # Formatar redes sociais
    social_media_str = ' | '.join(scrap_data.get('social_media_profiles', [])) if isinstance(scrap_data.get('social_media_profiles'), list) else ''

    # Remover campos com valores None
    dados_negocio = {
        "fields": {
            "TITLE": f"Via Automação - {razao_social} - CNPJ: {cnpj}",
            "UF_CRM_1729682188409": razao_social or '',
            "UF_CRM_1729682198513": nome_fantasia or '',
            "UF_CRM_1729682208297": cnpj or '',
            "UF_CRM_1729682242372": endereco or endereco_scrap or '',
            "UF_CRM_1729682256245": telefone1 or '',
            "UF_CRM_1729684520107": telefone2 or '',
            "UF_CRM_1729684527227": telefone3 or '',
            "UF_CRM_1729684539443": email or email_scrap or '',
            "UF_CRM_1729684551068": capital_social or '',
            "UF_CRM_1729684638352": socios_formatados or '',
            "UF_CRM_1730231431438": website if website != 'None' else '',
            "UF_CRM_1730231444951": social_media_str  # Redes Sociais formatadas como string
        }
    }
    # Remover quaisquer campos com valores vazios
    dados_negocio['fields'] = {k: v for k, v in dados_negocio['fields'].items() if v}

    # Fazer a requisição POST para criar o novo negócio no Bitrix24
    response = requests.post("https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.deal.add", json=dados_negocio)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        resultado = response.json()
        print(f"Negócio criado com sucesso! ID: {resultado['result']}")
    else:
        print(f"Erro ao criar negócio: {response.status_code}")

