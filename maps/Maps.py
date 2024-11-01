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

semaforo = threading.Semaphore(5)

# Função que configura o navegador e aplica o Selenium Stealth
def configurar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")

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
        # Espera até que o elemento de nome da empresa esteja visível antes de continuar
        nome_empresa = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
        ).text

        # Extrai as informações disponíveis
        dados_extracao = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")

        # Define valores default como None
        address = located_in = website = phone = None

        # Garante que não ocorra "index out of range"
        if len(dados_extracao) > 0:
            address = dados_extracao[0].text
        if len(dados_extracao) > 1:
            located_in = dados_extracao[1].text
        if len(dados_extracao) > 2:
            website = validate_website(dados_extracao[2].text)
        if len(dados_extracao) > 3:
            phone = format_phone(dados_extracao[3].text)

        page_url = driver.current_url

        # Retorna os dados extraídos como um dicionário
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
        # Retorna dicionário com valores None em caso de erro
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
        # Abrindo o Google Maps e pesquisando o termo desejado
        driver.get("https://www.google.com/maps")
        driver.find_element(By.ID, "searchboxinput").send_keys(termo_pesquisa + Keys.RETURN)

        # Verifica a presença de múltiplos resultados pela existência da classe específica
        time.sleep(2)  # Curta pausa para carregamento inicial de elementos
        if driver.find_elements(By.CLASS_NAME, "Nv2PK.tH5CWc.THOPZb"):
            # Caso haja múltiplos resultados, clicamos no primeiro não patrocinado
            if acessar_primeiro_resultado(driver):
                return extrair_dados(driver)
        else:
            # Extração direta se há apenas um resultado
            return extrair_dados(driver)

    finally:
        driver.quit()

# Função que gerencia as pesquisas usando threads, recebendo a lista de termos como parâmetro
def realizar_pesquisas(termos_de_pesquisa):
    resultados = []

    # Função auxiliar para adicionar resultados de uma thread
    def pesquisar_termo(termo):
        with semaforo:  # Limita a execução a 5 threads por vez
            resultado = pesquisa_google_maps(termo)
            if resultado:
                resultados.append(resultado)

    threads = []
    for termo in termos_de_pesquisa:
        thread = threading.Thread(target=pesquisar_termo, args=(termo,))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()

    return resultados