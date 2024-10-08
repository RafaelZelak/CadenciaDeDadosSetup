import aiohttp
import asyncio
from bs4 import BeautifulSoup
import random
import re
from tqdm.asyncio import tqdm_asyncio
from urllib.parse import urljoin
import phonenumbers
import requests
from collections import Counter
import json
import sys
import time

TIMEOUT = 20

phone_regex = r'\(?\+?[0-9]{1,4}\)?[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,9}'
address_regex = r'\d+\s[\w\s.-]+,\s?[A-Za-z\s]+,\s?[A-Za-z\s]+,\s?\d{5}(-\d{4})?'

# Função para capturar informações do Knowledge Graph
async def extract_knowledge_graph(soup):
    knowledge_data = {}

    # Capturando o título (nome do lugar)
    title_elem = soup.find('div', {'data-attrid': 'title'})
    if title_elem:
        knowledge_data['title'] = title_elem.get_text()

    # Capturando a nota
    rating_elem = soup.find('span', {'class': 'Aq14fc'})
    if rating_elem:
        knowledge_data['rating'] = rating_elem.get_text()

    # Capturando o número de avaliações
    review_count_elem = soup.find('span', {'class': 'hqzQac'})
    if review_count_elem:
        knowledge_data['review_count'] = review_count_elem.get_text()

    # Capturando a faixa de preço
    price_range_elem = soup.find('span', {'class': 'rRfnje'})
    if price_range_elem:
        knowledge_data['price_range'] = price_range_elem.get_text()

    # Capturando a descrição
    description_elem = soup.find('div', {'data-attrid': 'kc:/location/location:short_description'})
    if description_elem:
        knowledge_data['description'] = description_elem.get_text()

    # Capturando o endereço
    address_elem = soup.find('div', {'data-attrid': 'kc:/location/location:address'})
    if address_elem:
        knowledge_data['address'] = address_elem.get_text()

    # Capturando o telefone usando um seletor mais preciso
    phone_elem = soup.find('span', string=re.compile(r'^\(?\+?[0-9]{1,4}\)?[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,9}$'))
    if phone_elem:
        knowledge_data['phone'] = phone_elem.get_text()
    else:
        knowledge_data['phone'] = None

    # Capturando o horário de funcionamento
    hours_elem = soup.find('div', {'data-attrid': 'kc:/location/location:hours'})
    if hours_elem:
        raw_hours = hours_elem.get_text()
        knowledge_data['hours'] = formatar_horario_funcionamento(raw_hours)

    return knowledge_data

# Função para validar e formatar números de telefone
def validar_e_formatar_telefone(numero, regioes='BR'):
    try:
        numero_parseado = phonenumbers.parse(numero, regioes)
        if phonenumbers.is_valid_number(numero_parseado):
            formato_internacional = phonenumbers.format_number(numero_parseado, phonenumbers.PhoneNumberFormat.E164)
            formato_nacional = phonenumbers.format_number(numero_parseado, phonenumbers.PhoneNumberFormat.NATIONAL)
            return formato_internacional, formato_nacional
        else:
            return None, "Número inválido"
    except phonenumbers.NumberParseException as e:
        return None, str(e)

# Função para consultar e validar CEP
def consultar_cep(cep):
    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        if 'erro' in dados:
            return False, "CEP não encontrado"
        return True, dados
    else:
        return False, "Erro ao consultar CEP"

# Função assíncrona para realizar a busca no Google
async def google_search(query, session):
    google_search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A5341f Safari/604.1",
            "Mozilla/5.0 (Linux; U; Android 11; en-us; SM-N986U Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36"
        ]),
    }
    try:
        async with session.get(google_search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            results = []

            # Captura do Knowledge Graph, se disponível
            knowledge_graph_data = await extract_knowledge_graph(soup)
            if knowledge_graph_data:
                results.append({
                    'title': knowledge_graph_data.get('title', 'No title'),
                    'link': 'Info do Knowledge Graph',
                    'knowledge_data': knowledge_graph_data
                })

            # Capturar links dos resultados normais de busca
            for g in soup.find_all('div', class_='g'):
                title = g.find('h3').text if g.find('h3') else "No title"
                a_tag = g.find('a')
                link = a_tag['href'] if a_tag and a_tag.has_attr('href') else None
                snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else "No snippet"

                # Extração de possíveis telefones ou endereços no snippet de texto
                phone = re.findall(phone_regex, snippet)
                address = re.findall(address_regex, snippet)

                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                    'phone': phone[0] if phone else None,
                    'address': address[0] if address else None
                })

            return results

    except asyncio.TimeoutError:
        print(f"Timeout ao acessar {google_search_url}")
        return []
    except Exception as e:
        print(f"Erro ao acessar {google_search_url}: {e}")
        return []

def normalizar_social_media(url):
    # Regex para redes sociais (apenas perfil principal)
    patterns = {
        'facebook': r'https://(?:www\.)?facebook\.com/([^/?\s\'"<>]+)(?:/.*)?',
        'linkedin': r'https://(?:www\.)?linkedin\.com/(?:company/|in/)([^/?\s\'"<>]+)(?:/.*)?',
        'instagram': r'https://(?:www\.)?instagram\.com/([^/?\s\'"<>]+)(?:/.*)?'
    }

    for site, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return f'https://{site}.com/{match.group(1)}'

    return None

async def buscar_info_em_posts(url, session):
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
    }

    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            # Expressões regulares para encontrar e-mails e números de telefone
            email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            phone_regex = r'\(?\+?[0-9]{1,4}\)?[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,9}'

            # Encontrar e-mails e números de telefone no texto geral
            emails = re.findall(email_regex, soup.get_text())
            phones = re.findall(phone_regex, soup.get_text())

            # Encontrar e-mails e números de telefone em elementos específicos de posts
            post_elements = soup.find_all(['div', 'p', 'span'], string=True)
            for post in post_elements:
                post_text = post.get_text()
                emails.extend(re.findall(email_regex, post_text))
                phones.extend(re.findall(phone_regex, post_text))

            valid_emails = list(set(emails))
            valid_phones = []
            for phone in set(phones):
                internacional, nacional = validar_e_formatar_telefone(phone)
                if internacional:
                    valid_phones.append(internacional)
            valid_phones = list(set(valid_phones))

            return {
                'emails': valid_emails,
                'phones': valid_phones
            }
    except asyncio.TimeoutError:
        print(f"Timeout ao acessar {url}")
        return {'error': 'Timeout'}
    except Exception as e:
        return {'error': str(e)}

async def scrape_contact_info(url, session, deep_scan=False):
    if not url:
        return {'error': 'No URL provided'}

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
    }

    social_media_regex = r'(?:https?://(?:www\.)?(facebook|instagram|linkedin)\.com/[^?\s\'"<>]+)'

    try:
        social_media_profiles = {}
        if re.search(social_media_regex, url):
            normalized_url = normalizar_social_media(url)
            if normalized_url:
                key = normalized_url.split('/')[2]
                if key not in social_media_profiles:
                    social_media_profiles[key] = normalized_url

        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            phone_regex = r'\(?\+?[0-9]{1,4}\)?[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,4}[\s.-]?[0-9]{1,9}'
            address_regex = r'\d+\s[\w\s.-]+,\s?[A-Za-z\s]+,\s?[A-Za-z\s]+,\s?\d{5}(-\d{4})?'

            # Encontrar emails e telefones no conteúdo das postagens
            emails = re.findall(email_regex, soup.get_text())
            phones = re.findall(phone_regex, soup.get_text())
            addresses = re.findall(address_regex, soup.get_text())
            profiles = re.findall(social_media_regex, soup.get_text())

            # Procurar informações em postagens específicas (exemplo genérico, ajustar conforme a estrutura da página)
            post_elements = soup.find_all('div', {'class': 'x11i5rnm'})  # Ajustar seletor conforme necessário
            for post in post_elements:
                post_text = post.get_text()
                emails.extend(re.findall(email_regex, post_text))
                phones.extend(re.findall(phone_regex, post_text))

            for profile in profiles:
                normalized_url = normalizar_social_media(f'https://{profile[0]}.com/{profile[1]}')
                if normalized_url:
                    key = normalized_url.split('/')[2]
                    if key not in social_media_profiles:
                        social_media_profiles[key] = normalized_url

        # Filtrar para garantir que apenas perfis principais sejam retornados
        valid_social_media_profiles = {}
        for key, url in social_media_profiles.items():
            if 'photo.php' in url or 'p/' in url:
                continue  # Ignorar links de fotos ou vídeos
            valid_social_media_profiles[key] = url

        emails = list(set(emails))
        valid_phones = []
        for phone in set(phones):
            internacional, nacional = validar_e_formatar_telefone(phone)
            if internacional:
                valid_phones.append(internacional)
        valid_phones = list(set(valid_phones))

        addresses = list(set(addresses))
        social_media_profiles = list(set(valid_social_media_profiles.values()))

        contact_info = {
            'emails': emails,
            'phones': valid_phones,
            'addresses': addresses,
            'social_media_profiles': social_media_profiles
        }

        # Realiza varredura profunda, se necessário
        return contact_info
    except asyncio.TimeoutError:
        print(f"Timeout ao acessar {url}")
        return {'error': 'Timeout'}
    except Exception as e:
        return {'error': str(e)}

# Função para formatar o horário de funcionamento
def formatar_horario_funcionamento(horarios_raw):
    if isinstance(horarios_raw, str):
        # Remover partes desnecessárias e formatar corretamente
        horarios_limp = re.sub(r"Horário de funcionamento: Aberto ⋅ ", "", horarios_raw)
        horarios_limp = re.sub(r"Sugerir novos horários.*$", "", horarios_limp)

        # Adicionar quebras de linha entre os dias da semana
        horarios_limp = re.sub(r'(segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo)', r'\n\1', horarios_limp)

        # Remover prefixos como "00"
        horarios_limp = re.sub(r'00(\w+-feira)', r'\1', horarios_limp)

        # Separar "Fechado" corretamente dos dias da semana
        horarios_limp = re.sub(r'(Fechado)(\w+-feira)', r'\1\n\2', horarios_limp)

        # Dividir a string em linhas e processar cada linha
        linhas = horarios_limp.strip().split("\n")
        horarios_dict = {}

        for linha in linhas:
            # Encontrar dias da semana e horários usando regex
            match = re.match(r'(segunda-feira|terça-feira|quarta-feira|quinta-feira|sexta-feira|sábado|domingo)\s*(\d{2}:\d{2}–\d{2}:\d{2}|Fechado)', linha)
            if match:
                dia, horario = match.groups()
                horarios_dict[dia] = horario

        return horarios_dict

    elif isinstance(horarios_raw, dict):
        # Se os horários já estiverem no formato de dicionário
        return horarios_raw

    return None

# Função para consolidar as informações coletadas
def consolidar_informacoes(knowledge_data, contact_infos):
    # Inicializar os contadores para os dados
    emails_counter = Counter()
    phones_counter = Counter()
    addresses_counter = Counter()
    social_media_profiles = []

    # Preencher os contadores com as informações extraídas
    for contact_info in contact_infos:
        if 'emails' in contact_info:
            emails_counter.update(contact_info['emails'])
        if 'phones' in contact_info:
            phones_counter.update(contact_info['phones'])
        if 'addresses' in contact_info:
            addresses_counter.update(contact_info['addresses'])
        if 'social_media_profiles' in contact_info:
            social_media_profiles.extend(contact_info['social_media_profiles'])  # Redes sociais

    # Escolher os valores mais comuns ou usar os do Knowledge Graph
    email_final = knowledge_data.get('email') or (emails_counter.most_common(1)[0][0] if emails_counter else None)
    phone_final = knowledge_data.get('phone') or (phones_counter.most_common(1)[0][0] if phones_counter else None)
    address_final = knowledge_data.get('address') or (addresses_counter.most_common(1)[0][0] if addresses_counter else None)

    # Adicionar redes sociais do Knowledge Graph, se existirem
    if knowledge_data.get('social_media_profiles'):
        social_media_profiles.extend(knowledge_data['social_media_profiles'])

    # Remover duplicatas das redes sociais
    social_media_profiles = list(set(social_media_profiles))

    # Formatar o horário de funcionamento
    hours_final = None
    if 'hours' in knowledge_data:
        hours_final = formatar_horario_funcionamento(knowledge_data['hours'])

    # Retornar as informações consolidadas
    return {
        'email': email_final,
        'phone': phone_final,
        'address': address_final,
        'social_media_profiles': social_media_profiles,
        'hours': hours_final
    }

# Função para processar uma única query
async def process_single_query(query, session, progress_bar):
    print(f"Processando query: {query}", flush=True)

    try:
        resultados = await asyncio.wait_for(google_search(query, session), timeout=TIMEOUT)

        tasks = []
        for resultado in resultados:
            link = resultado.get('link', '')
            if link and "http" in link:
                tasks.append(scrape_contact_info(link, session, deep_scan=True))

        contact_infos = []
        if tasks:
            for info in await asyncio.gather(*tasks):
                contact_infos.append(info)

        knowledge_graph_data = None
        for resultado in resultados:
            if 'knowledge_data' in resultado:
                knowledge_graph_data = resultado['knowledge_data']
                break

        if knowledge_graph_data and 'hours' in knowledge_graph_data:
            knowledge_graph_data['hours'] = formatar_horario_funcionamento(knowledge_graph_data['hours'])

        informacoes_consolidadas = consolidar_informacoes(knowledge_graph_data or {}, contact_infos)

        resultado_json = {
            "knowledge_graph": knowledge_graph_data,
            "consolidated_contact_info": informacoes_consolidadas
        }

        return json.dumps(resultado_json, indent=4, ensure_ascii=False)
    except asyncio.TimeoutError:
        print(f"Timeout ao processar query: {query}")
    finally:
        progress_bar.update(1)  # Atualizar a barra global após processar a query
    return None

# Função principal para processar várias queries
async def process_queries(queries):
    total_queries = len(queries)

    async with aiohttp.ClientSession() as session:
        start_time = time.time()  # Tempo de início
        with tqdm_asyncio(total=total_queries, desc="Processing queries") as global_pbar:
            tasks = [process_single_query(query, session, global_pbar) for query in queries]

            # Coletar resultados e garantir que as barras de progresso sejam fechadas antes de imprimir
            resultados = await asyncio.gather(*tasks)

            # Retorna os resultados para serem usados externamente
            return resultados

        end_time = time.time()  # Tempo de término
        elapsed_time = end_time - start_time  # Tempo decorrido
        print(f"\nTempo total de execução: {elapsed_time:.2f} segundos")