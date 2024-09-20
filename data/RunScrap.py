import asyncio
import json
import csv
from WebScrapSelenium import run_scraping_multiple
from WebScrapBeautifulSoup import run_beautifulsoup_scraping
from tqdm.asyncio import tqdm_asyncio
import time
import os

async def combine_results(selenium_data, beautifulsoup_data):
    # Verificar se os dados do BeautifulSoup são válidos
    if beautifulsoup_data is None:
        bs_data = {}
    else:
        try:
            bs_data = json.loads(beautifulsoup_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Erro ao carregar BeautifulSoup data: {e}")
            bs_data = {}

    # Garantir que bs_data seja um dicionário e não None
    if not isinstance(bs_data, dict):
        bs_data = {}

    # Garantir que bs_data sempre tenha um dicionário para consolidated_contact_info
    consolidated_contact_info = bs_data.get("consolidated_contact_info", {})

    # Garantir que consolidated_contact_info não seja None
    if not isinstance(consolidated_contact_info, dict):
        consolidated_contact_info = {}

    # Verificar se existe um knowledge_graph e lidar com a ausência dele
    knowledge_graph = bs_data.get("knowledge_graph", {})
    if not isinstance(knowledge_graph, dict):
        knowledge_graph = {}

    # Combinar redes sociais de Selenium e BeautifulSoup e remover duplicatas
    combined_social_media = list(set(selenium_data.get("social_media_profiles", []) + consolidated_contact_info.get("social_media_profiles", [])))

    # Normalizar URLs de redes sociais, removendo trailing slashes ou subpaths desnecessários
    normalized_social_media = []
    for profile in combined_social_media:
        # Normaliza URLs removendo subpaths como "/img" ou barras extras
        profile = profile.split("?")[0]  # Remove parâmetros
        profile = profile.rstrip("/")  # Remove barras extras no final
        if profile not in normalized_social_media:
            normalized_social_media.append(profile)

    # Criar o dicionário consolidado usando os dados disponíveis
    consolidated_data = {
        "name": knowledge_graph.get("title", ""),  # Ignora se não tiver título
        "rating": knowledge_graph.get("rating", ""),  # Ignora se não tiver rating
        "review_count": knowledge_graph.get("review_count", ""),  # Ignora se não tiver review_count
        "address": consolidated_contact_info.get("address", None),
        "phone": selenium_data.get("phone", consolidated_contact_info.get("phone", "")),
        "email": selenium_data.get("email", consolidated_contact_info.get("email", [])),
        "hours": consolidated_contact_info.get("hours", None),
        "social_media_profiles": normalized_social_media
    }

    return consolidated_data

async def main():
    csv_file_path = os.path.join(os.path.dirname(__file__), 'dados_fracos.csv')
    # Carregar os dados do CSV
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        empresas = [row for row in reader]

    resultados_enriquecidos = []

    start_time = time.time()

    # Fazer a pesquisa para cada empresa
    for empresa in empresas:
        query = f"{empresa['Empresa']} {empresa['Município']}"
        print(f"\nIniciando scraping para: {query}")

        # Rodar o scraping com Selenium e BeautifulSoup em paralelo
        selenium_task = asyncio.to_thread(run_scraping_multiple, [query])
        beautifulsoup_task = run_beautifulsoup_scraping([query])

        # Exibir barra de progresso enquanto a tarefa executa
        selenium_results, beautifulsoup_results = await tqdm_asyncio.gather(
            selenium_task,
            beautifulsoup_task,
            desc=f"Processando scraping para {query}",
            total=2
        )

        # Combinar os resultados do Selenium e BeautifulSoup
        selenium_result = selenium_results.get(query, {})
        beautifulsoup_result = beautifulsoup_results[0]  # Assumimos que a posição 0 é para este query
        combined_result = await combine_results(selenium_result, beautifulsoup_result)

        # Adicionar username ao resultado combinado
        combined_result['username'] = empresa['Username']

        # Armazenar o resultado para salvar posteriormente
        resultados_enriquecidos.append(combined_result)

    # Salvar os resultados no CSV de saída
    with open('data/dados_enriquecidos.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'rating', 'review_count', 'address', 'phone', 'email', 'hours', 'social_media_profiles', 'username']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for resultado in resultados_enriquecidos:
            writer.writerow(resultado)

    # Calcular o tempo total de execução
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTempo total de execução: {total_time:.2f} segundos")

if __name__ == "__main__":
    asyncio.run(main())
