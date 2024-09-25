import asyncio
import json
import csv
from WebScrapSelenium import run_scraping_multiple
from WebScrapBeautifulSoup import run_beautifulsoup_scraping
from tqdm.asyncio import tqdm_asyncio
import time
import os
import psycopg2
import logging
# Função para conectar ao banco de dados PostgreSQL
def connect_to_db():
    return psycopg2.connect(
        user="postgres",
        password="r1r2r3r4r5",
        host="127.0.0.1",
        port="5432",
        database="EnrichedData"
    )

# Função para buscar o User ID pelo username
def get_user_id(cursor, username):
    cursor.execute('SELECT "id" FROM "Users" WHERE "username" = %s', (username,))
    result = cursor.fetchone()
    return result[0] if result else None

# Função para verificar se a query já existe no banco de dados
def query_already_exists(cursor, query):
    cursor.execute('SELECT 1 FROM "Result" WHERE "enterprise" = %s', (query,))
    return cursor.fetchone() is not None

# Função para inserir o resultado enriquecido no banco de dados, incluindo a query
def insert_enriched_data(cursor, user_id, data, query):
    try:
        # Certifique-se de usar o nome exato da tabela e colunas, com aspas duplas se necessário
        query_sql = '''
            INSERT INTO "Result" ("userid", "name", "rating", "review_count", "address",
                                  "phone", "email", "hours", "social_media_profiles", "enterprise", "enviado_bitrix")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(query_sql, (
            user_id,
            data.get("name", ""),
            data.get("rating", ""),
            data.get("review_count", ""),
            data.get("address", ""),
            data.get("phone", ""),
            json.dumps(data.get("email", [])),
            json.dumps(data.get("hours", {})),
            json.dumps(data.get("social_media_profiles", [])),
            query,
            False
        ))
        print(f"Dados inseridos com sucesso para o usuário ID {user_id}")
    except Exception as e:
        logging.error(f"Erro ao inserir dados enriquecidos: {e}")

# Função para combinar resultados de Selenium e BeautifulSoup
async def combine_results(selenium_data, beautifulsoup_data):
    # Mesma lógica existente para combinar os dados
    if beautifulsoup_data is None:
        bs_data = {}
    else:
        try:
            bs_data = json.loads(beautifulsoup_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Erro ao carregar BeautifulSoup data: {e}")
            bs_data = {}

    consolidated_contact_info = bs_data.get("consolidated_contact_info", {})
    if not isinstance(consolidated_contact_info, dict):
        consolidated_contact_info = {}

    knowledge_graph = bs_data.get("knowledge_graph", {})
    if not isinstance(knowledge_graph, dict):
        knowledge_graph = {}

    combined_social_media = list(set(selenium_data.get("social_media_profiles", []) + consolidated_contact_info.get("social_media_profiles", [])))

    normalized_social_media = []
    for profile in combined_social_media:
        profile = profile.split("?")[0]
        profile = profile.rstrip("/")
        if profile not in normalized_social_media:
            normalized_social_media.append(profile)

    consolidated_data = {
        "name": knowledge_graph.get("title", ""),
        "rating": knowledge_graph.get("rating", ""),
        "review_count": knowledge_graph.get("review_count", ""),
        "address": consolidated_contact_info.get("address", None),
        "phone": selenium_data.get("phone", consolidated_contact_info.get("phone", "")),
        "email": selenium_data.get("email", consolidated_contact_info.get("email", [])),
        "hours": consolidated_contact_info.get("hours", None),
        "social_media_profiles": normalized_social_media
    }

    return consolidated_data

# Função principal que executa o scraping e insere no banco, incluindo a query
async def main():
    csv_file_path = os.path.join(os.path.dirname(__file__), 'dados_fracos.csv')
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        empresas = [row for row in reader]

    # Conectar ao banco de dados
    conn = connect_to_db()
    cursor = conn.cursor()

    start_time = time.time()

    for empresa in empresas:
        query = f"{empresa['Empresa']} {empresa['Município']}"

        # Verificar se a query já foi realizada
        if query_already_exists(cursor, query):
            print(f"Query '{query}' já foi realizada anteriormente. Pulando scraping.")
            continue

        print(f"\nIniciando scraping para: {query}")

        selenium_task = asyncio.to_thread(run_scraping_multiple, [query])
        beautifulsoup_task = run_beautifulsoup_scraping([query])

        selenium_results, beautifulsoup_results = await tqdm_asyncio.gather(
            selenium_task,
            beautifulsoup_task,
            desc=f"Processando scraping para {query}",
            total=2
        )

        selenium_result = selenium_results.get(query, {})
        beautifulsoup_result = beautifulsoup_results[0]
        combined_result = await combine_results(selenium_result, beautifulsoup_result)

        username = empresa['Username']
        user_id = get_user_id(cursor, username)

        if user_id:
            insert_enriched_data(cursor, user_id, combined_result, query)  # Passando a query para a função
        else:
            print(f"Usuário {username} não encontrado.")

    conn.commit()  # Confirmar as transações
    cursor.close()
    conn.close()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTempo total de execução: {total_time:.2f} segundos")

if __name__ == "__main__":
    asyncio.run(main())