import random
import cloudscraper

# Lista de proxies
proxies_list = [
    {"ip": "18.228.198.164", "port": 80},
    {"ip": "165.232.129.150", "port": 80},
    {"ip": "46.51.249.135", "port": 3128},
    {"ip": "87.98.148.98", "port": 80},
    {"ip": "20.205.61.143", "port": 80},
    {"ip": "13.36.113.81", "port": 3128},
    {"ip": "129.226.193.16", "port": 3128},
    {"ip": "91.241.217.58", "port": 9090},
    {"ip": "79.110.201.235", "port": 8081},
    {"ip": "3.122.84.99", "port": 3128},
    {"ip": "158.255.77.169", "port": 80},
    {"ip": "41.196.0.163", "port": 8082},
    {"ip": "3.129.184.210", "port": 3128},
    {"ip": "80.249.112.162", "port": 80},
    {"ip": "38.54.116.9", "port": 9080},
    {"ip": "185.164.73.117", "port": 80},
    {"ip": "51.210.54.186", "port": 80},
    {"ip": "13.37.73.214", "port": 80},
    {"ip": "8.220.205.172", "port": 3128},
    {"ip": "20.111.54.16", "port": 8123},
    {"ip": "198.49.68.80", "port": 80},
    {"ip": "8.215.12.103", "port": 8008},
    {"ip": "8.213.195.191", "port": 9080},
    {"ip": "18.228.198.164", "port": 3128},
    {"ip": "3.124.133.93", "port": 3128},
    {"ip": "178.48.68.61", "port": 18080},
    {"ip": "8.215.3.250", "port": 8080},
    {"ip": "8.213.151.128", "port": 3128},
    {"ip": "87.248.129.26", "port": 80},
    {"ip": "13.38.153.36", "port": 80},
    {"ip": "43.134.229.98", "port": 3128},
    {"ip": "162.223.90.130", "port": 80},
    {"ip": "8.220.205.172", "port": 8081},
    {"ip": "188.32.100.60", "port": 8080},
    {"ip": "3.129.184.210", "port": 80},
]

# Função para testar se um proxy responde com status 200 usando cloudscraper
def testar_proxy(ip, port):
    proxy = {
        "http": f"http://{ip}:{port}",
        "https": f"https://{ip}:{port}"
    }
    scraper = cloudscraper.create_scraper()
    try:
        print(f"Tentando testar proxy: {ip}:{port}")
        response = scraper.get("http://httpbin.org/ip", proxies=proxy, timeout=5)
        print(f"Status do proxy {ip}:{port}: {response.status_code}")
        if response.status_code == 200:
            print(f"Proxy {ip}:{port} está funcional.")
            return proxy
        else:
            print(f"Proxy {ip}:{port} retornou status {response.status_code}.")
    except Exception as e:
        print(f"Erro ao testar proxy {ip}:{port}: {e}")
    return None

# Função para obter um proxy funcional aleatoriamente, com até 3 tentativas
def obter_proxy():
    tentativas = 3
    for tentativa in range(tentativas):
        print(f"Tentativa {tentativa + 1} de {tentativas} para obter proxy.")
        proxy = random.choice(proxies_list)
        proxy_funcional = testar_proxy(proxy["ip"], proxy["port"])
        if proxy_funcional:
            return proxy_funcional
    print("Nenhum proxy funcional encontrado após 3 tentativas. Usando IP local.")
    return None

# Função para fazer a requisição POST à API da Casa de Dados usando cloudscraper
def obter_dados_cnpj(termos_expandidos, estado=None, cidade=None, page=1):
    proxy = obter_proxy()  # Tenta obter um proxy funcional
    scraper = cloudscraper.create_scraper()

    url = "https://api.casadosdados.com.br/v2/public/cnpj/search"
    data = {
        "query": {
            "termo": termos_expandidos,
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
        # Realiza a requisição POST com proxy (se disponível)
        if proxy:
            response = scraper.post(url, json=data, proxies=proxy, verify=False, timeout=10)
        else:
            response = scraper.post(url, json=data, verify=False, timeout=10)

        # Processa a resposta
        if response.status_code == 200:
            print("Dados recebidos com sucesso:")
            return response.json()
        else:
            print(f"Erro na requisição: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao fazer a requisição para a API: {e}")
    return None

# Exemplo de uso
termos_expandidos = "Setup Tecnologia"
estado = "PR"
cidade = "Curitiba"
page = 1

dados = obter_dados_cnpj(termos_expandidos, estado, cidade, page)
if dados:
    print(dados)
