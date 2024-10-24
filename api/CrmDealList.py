import requests

def verificar_negocio_existente(cnpj):
    bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.deal.list.json"

    # Parâmetros para buscar negócios com base no CNPJ
    params = {
        "filter": {
            "UF_CRM_1729682208297": cnpj  # Campo de CNPJ no Bitrix
        },
        "select": ["ID", "TITLE", "UF_CRM_1729682208297"]  # Seleciona o ID e Título do Negócio
    }

    # Fazer a requisição POST para verificar se o negócio já existe
    try:
        response = requests.post(bitrix_url, json=params)

        if response.status_code == 200:
            resultado = response.json()

            # Verifica se há negócios com o CNPJ informado
            if 'result' in resultado and len(resultado['result']) > 0:
                negocio = resultado['result'][0]  # Pega o primeiro resultado (caso haja múltiplos)
                lead_id = negocio['ID']
                lead_link = f"https://setup.bitrix24.com.br/crm/deal/details/{lead_id}/"
                return True, lead_link
            else:
                print("Nenhum negócio existente com este CNPJ.")
                return False, None
        else:
            print(f"Erro ao verificar negócio existente: {response.status_code} - {response.text}")
            return False, None

    except Exception as e:
        print(f"Erro durante a requisição: {e}")
        return False, None
