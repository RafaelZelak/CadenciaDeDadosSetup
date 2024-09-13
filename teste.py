import requests
from bs4 import BeautifulSoup
import random
import re
import time

# Função para realizar a busca no Google e tentar capturar informações do Knowledge Graph
def google_search(query):
    google_search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
    }

    response = requests.get(google_search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    # Tentar capturar informações do Knowledge Graph (caixa lateral do Google)
    knowledge_graph = soup.find('div', {'data-attrid': 'kc:/local:onebox'})
    if knowledge_graph:
        title_elem = knowledge_graph.find('span', {'class': 'BNeawe tAd8D AP7Wnd'})
        contact_elem = knowledge_graph.find('span', {'class': 'BNeawe s3v9rd AP7Wnd'})
        business_info = {
            'title': title_elem.text if title_elem else "No title",
            'contact': contact_elem.text if contact_elem else "No contact info"
        }
        results.append(business_info)
    else:
        print("Knowledge Graph não encontrado.")

    # Extrair links dos resultados normais de busca
    for g in soup.find_all('div', class_='g'):
        title = g.find('h3').text if g.find('h3') else "No title"
        a_tag = g.find('a')
        link = a_tag['href'] if a_tag and a_tag.has_attr('href') else "No link"
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else "No snippet"
        results.append({'title': title, 'link': link, 'snippet': snippet})

    return results

# Função para extrair informações de contato de uma página
def scrape_contact_info(url):
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Expressões regulares para capturar email, telefone e outros dados
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_regex = r'\(?\+?[0-9]{1,4}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}'
        address_regex = r'[\w\s,-]+,\s?[A-Za-z]{2,}\s?\d{5}-?\d{3}'
        social_media_regex = r'(facebook|instagram|linkedin|twitter)\.com/[^\'"\s]+'

        # Extraindo emails, telefones, endereços e redes sociais
        emails = re.findall(email_regex, soup.text)
        phones = re.findall(phone_regex, soup.text)
        addresses = re.findall(address_regex, soup.text)
        social_media_profiles = re.findall(social_media_regex, soup.text)

        # Buscar links de páginas de "Contato" ou outras páginas relevantes
        contact_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].lower()
            if any(term in href for term in ['contact', 'contato', 'about', 'sobre', 'support', 'suporte']):
                contact_links.append(href)
            if 'mailto:' in href:
                emails.append(href.replace('mailto:', ''))

        # Seguir links de contato e tentar extrair mais informações
        for contact_link in contact_links:
            if not contact_link.startswith('http'):
                contact_link = url + contact_link  # Corrigir links relativos
            contact_response = requests.get(contact_link, headers=headers)
            contact_soup = BeautifulSoup(contact_response.text, "html.parser")
            emails += re.findall(email_regex, contact_soup.text)
            phones += re.findall(phone_regex, contact_soup.text)
            addresses += re.findall(address_regex, contact_soup.text)
            social_media_profiles += re.findall(social_media_regex, contact_soup.text)

        # Remover duplicatas e limpar dados irrelevantes
        emails = list(set(emails))
        phones = list(set(phones))
        addresses = list(set(addresses))
        social_media_profiles = list(set(social_media_profiles))

        # Filtrar endereços irrelevantes
        addresses = [addr for addr in addresses if len(addr.split()) > 2 and not re.search(r'\bsemana\b|\bmensagem\b|\breceber\b|\bcaptar\b', addr)]

        # Filtrar e formatar números de telefone
        phones = [phone for phone in phones if re.match(r'^\(?\+?[0-9]{1,4}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}$', phone)]

        return {
            'emails': emails,
            'phones': phones,
            'addresses': addresses,
            'social_media_profiles': social_media_profiles,
            'contact_links': contact_links
        }
    except Exception as e:
        return {'error': str(e)}

# Exemplo de uso
query = "Setup Tecnologia"
resultados = google_search(query)
for resultado in resultados:
    print(f"Título: {resultado.get('title')}")
    print(f"Link: {resultado.get('link', 'Info do Knowledge Graph')}")
    contact_info = scrape_contact_info(resultado.get('link', ''))
    print(f"Emails: {contact_info.get('emails', 'No emails found')}")
    print(f"Phones: {contact_info.get('phones', 'No phones found')}")
    print(f"Addresses: {contact_info.get('addresses', 'No addresses found')}")
    print(f"Social Media Profiles: {contact_info.get('social_media_profiles', 'No profiles found')}")
    print(f"Links de Contato: {contact_info.get('contact_links', 'No contact links found')}")
    print("-" * 60)
    time.sleep(random.uniform(.1, .5))
