import requests
from bs4 import BeautifulSoup

# Lista de países mais próximos do Brasil (em termos de latência geográfica)
low_latency_countries = ['BR', 'AR', 'CL', 'CO', 'UY', 'PY', 'PE', 'BO', 'EC']

def get_proxies():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)

    if response.status_code != 200:
        return []  # Retorna uma lista vazia em caso de erro

    soup = BeautifulSoup(response.text, 'html.parser')

    proxies = []
    rows = soup.find_all("tr")

    for row in rows[1:]:  # Ignora o cabeçalho
        cols = row.find_all("td")
        if len(cols) >= 7:
            ip = cols[0].text
            port = cols[1].text
            country_code = cols[2].text.strip()  # Código do país está na terceira coluna
            https = cols[6].text.strip() == 'yes'
            proxy_type = 'https' if https else 'http'
            proxy = {
                'proxy': f"{proxy_type}://{ip}:{port}",
                'country': country_code
            }
            proxies.append(proxy)

    return proxies

def filter_proxies_by_country(proxies):
    # Filtra proxies de países com baixa latência
    filtered_proxies = [proxy for proxy in proxies if proxy['country'] in low_latency_countries]
    return filtered_proxies[:50]

def make_request_with_proxy(proxy):
    try:
        proxies = {
            "http": proxy,
            "https": proxy
        }
        # Faz a requisição ao Google usando o proxy
        response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
        return response.status_code == 200  # Retorna True se o status for 200 (sucesso)
    except requests.exceptions.RequestException:
        return False  # Retorna False em caso de erro

def get_working_proxies():
    # Pega a lista de proxies
    proxies = get_proxies()

    # Filtra os proxies de países próximos ao Brasil
    selected_proxies = filter_proxies_by_country(proxies)

    # Lista para armazenar proxies que funcionam
    successful_proxies = []

    if selected_proxies:
        for proxy_info in selected_proxies:
            if make_request_with_proxy(proxy_info['proxy']):
                successful_proxies.append(proxy_info['proxy'])

    return successful_proxies  # Retorna a lista de proxies que funcionaram

# Exemplo de uso da função em outro arquivo
if __name__ == "__main__":
    working_proxies = get_working_proxies()
    print(working_proxies)  # Apenas para verificar a saída
