from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import phonenumbers
import validators
import time
import threading
import psutil
from tqdm import tqdm


semaforo = threading.Semaphore(2)

# Função que configura o navegador e aplica o Selenium Stealth
def configurar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
    )
    return driver

# Função para encerrar processos do Chrome e ChromeDriver que possam ter ficado ativos
def encerrar_processos_restantes():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in ('chrome', 'chromedriver'):
            proc.kill()

# Função para formatar telefone
def format_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, "BR")
        if phonenumbers.is_possible_number(parsed_phone):
            return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
    except phonenumbers.NumberParseException:
        pass
    return None

# Função para validar website
def validate_website(url):
    return url if validators.url(url) else "None"

# Função para acessar o primeiro resultado válido (não patrocinado)
def acessar_primeiro_resultado(driver):
    resultados = driver.find_elements(By.CLASS_NAME, "Nv2PK.tH5CWc.THOPZb")
    for resultado in resultados:
        if resultado.find_elements(By.XPATH, ".//span[contains(text(), 'Patrocinado')]"):
            continue
        link = resultado.find_element(By.CLASS_NAME, "hfpxzc")
        link.click()

        # Espera ativa para verificar a presença dos elementos da empresa
        start_time = time.time()
        while time.time() - start_time < 10:
            if driver.find_elements(By.CLASS_NAME, "Io6YTe"):
                return True
            time.sleep(0.05)
        return False

# Função para extrair dados da empresa
def extrair_dados(driver):
    try:
        nome_empresa = WebDriverWait(driver, 10, poll_frequency=0.5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
        ).text

        dados_extracao = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")
        address = located_in = website = phone = None

        if len(dados_extracao) > 0:
            address = dados_extracao[0].text
        if len(dados_extracao) > 1:
            located_in = dados_extracao[1].text
        if len(dados_extracao) > 2:
            website = validate_website(dados_extracao[2].text)
        if len(dados_extracao) > 3:
            phone = format_phone(dados_extracao[3].text)

        page_url = driver.current_url

        print(f"\nnome_empresa:{nome_empresa}\naddress:{address}\nlocated:{located_in}\nwebsite:{website}\nphone:{phone}\npage_url:{page_url}")
        return {
            "title_maps": nome_empresa,
            "address_maps": address,
            "located_maps": located_in,
            "website_maps": website,
            "phone_maps": phone,
            "page_url_maps": page_url
        }

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return {
            "title_maps": None,
            "address_maps": None,
            "located_maps": None,
            "website_maps": None,
            "phone_maps": None,
            "page_url_maps": None
        }

# Função principal para pesquisa
def pesquisa_google_maps(termo_pesquisa):
    driver = configurar_driver()

    try:
        driver.get("https://www.google.com/maps")
        driver.find_element(By.ID, "searchboxinput").send_keys(termo_pesquisa + Keys.RETURN)

        time.sleep(2)
        if driver.find_elements(By.CLASS_NAME, "Nv2PK.tH5CWc.THOPZb"):
            if acessar_primeiro_resultado(driver):
                return extrair_dados(driver)
        else:
            return extrair_dados(driver)

    finally:
        driver.quit()
        encerrar_processos_restantes()  # Garante o fechamento de processos

# Função que gerencia as pesquisas usando threads
def realizar_pesquisas(termos_de_pesquisa):
    resultados = []
    total_pesquisas = len(termos_de_pesquisa)  # Total de pesquisas para a barra de progresso

    # Função interna para realizar a pesquisa
    def pesquisar_termo(termo, index, pbar):
        with semaforo:
            resultado = pesquisa_google_maps(termo)
            if resultado:
                resultados.append(resultado)
            if index % 10 == 0:
                encerrar_processos_restantes()  # Reinicia processos a cada 10 pesquisas para otimizar memória
            time.sleep(1)  # Pausa de 1 segundo para reduzir a carga
            pbar.update(1)  # Atualiza a barra de progresso

    # Inicia a barra de progresso com o total de termos a serem pesquisados
    with tqdm(total=total_pesquisas, desc="Progresso das pesquisas", unit="pesquisa") as pbar:
        threads = []
        for i, termo in enumerate(termos_de_pesquisa):
            thread = threading.Thread(target=pesquisar_termo, args=(termo, i, pbar))
            threads.append(thread)
            thread.start()

        # Aguarda todas as threads terminarem
        for thread in threads:
            thread.join()

    return resultados
