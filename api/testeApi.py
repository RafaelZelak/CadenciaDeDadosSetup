import requests

# URL da API do Bitrix24 para criar um novo negócio


# Função para criar o negócio com os parâmetros recebidos
def criar_negocio(razao_social, nome_fantasia, cnpj, endereco, telefone1, telefone2, telefone3, email, capital_social, socios):
    # Dados do novo negócio
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.deal.add"
    dados_negocio = {
        "fields": {
            "TITLE": f"{razao_social} - {nome_fantasia} - CNPJ: {cnpj}",
            "UF_CRM_1729682188409": razao_social,    # Razão Social
            "UF_CRM_1729682198513": nome_fantasia,   # Nome Fantasia
            "UF_CRM_1729682208297": cnpj,            # CNPJ
            "UF_CRM_1729682242372": endereco,        # Endereço
            "UF_CRM_1729682256245": telefone1,       # Telefone 1 (ID correto)
            "UF_CRM_1729684520107": telefone2,       # Telefone 2
            "UF_CRM_1729684527227": telefone3,       # Telefone 3
            "UF_CRM_1729684539443": email,           # E-mail
            "UF_CRM_1729684551068": capital_social,  # Capital Social
            "UF_CRM_1729684638352": socios           # Sócios
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
        print(response.text)

# Exemplo de chamada da função com placeholders
criar_negocio(
    razao_social="Via Automação - Empresa Exemplo Ltda.",
    nome_fantasia="Via Automação",
    cnpj="27163364000149",
    endereco="Rua Exemplo, 123 - São Paulo, SP",
    telefone1="(11) 1234-5678",       # Telefone 1
    telefone2="(11) 8765-4321",       # Telefone 2
    telefone3="(11) 5555-5555",       # Telefone 3
    email="contato@viaautomacao.com.br",
    capital_social="1000000",         # Capital Social em valor monetário
    socios="Nome do Sócio 1 | Qualificação 1, Nome do Sócio 2 | Qualificação 2"
)
