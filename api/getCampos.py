import requests
import json

# URL da API do Bitrix24 para listar os campos
bitrix_url = "https://setup.bitrix24.com.br/rest/197/z8mt11u0z5wq34y5/crm.deal.fields"

# Fazer a requisição GET para listar os campos do CRM
response = requests.get(bitrix_url)

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    fields = response.json().get('result', {})

    # Imprimir todos os campos com detalhes
    for field_id, field_info in fields.items():
        print(f"ID: {field_id}")
        print(json.dumps(field_info, indent=4))  # Exibir todos os detalhes do campo de forma organizada
        print("\n")
else:
    print(f"Erro: {response.status_code}")
