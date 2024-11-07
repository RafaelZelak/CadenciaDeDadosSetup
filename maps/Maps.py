import logging
import threading
import time
import psutil
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import phonenumbers
import validators

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
lock = threading.Lock()

semaforo = threading.Semaphore(2)

def configurar_driver():
    with lock:
        logging.info("Configurando o driver do Chrome")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("user-agent=Mozilla/5.0")

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

def encerrar_processos_restantes():
    with lock:
        logging.info("Encerrando processos Chrome e ChromeDriver restantes")
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in ('chrome', 'chromedriver'):
            try:
                proc.kill()
            except psutil.Error as e:
                with lock:
                    logging.warning(f"Erro ao encerrar processo {proc.info['name']}: {e}")

def format_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, "BR")
        if phonenumbers.is_possible_number(parsed_phone):
            return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
    except phonenumbers.NumberParseException:
        pass
    return None

def validate_website(url):
    return url if validators.url(url) else "None"

def acessar_primeiro_resultado(driver):
    resultados = driver.find_elements(By.CLASS_NAME, "Nv2PK.tH5CWc.THOPZb")
    for index, resultado in enumerate(resultados):
        try:
            if resultado.find_elements(By.XPATH, ".//span[contains(text(), 'Patrocinado')]"):
                continue
            link = resultado.find_element(By.CLASS_NAME, "hfpxzc")
            link.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "Io6YTe")))
            return True
        except Exception:
            continue
    return False

def extrair_dados(driver):
    try:
        nome_empresa = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
        ).text
        dados_extracao = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")

        address = dados_extracao[0].text if len(dados_extracao) > 0 else None
        located_in = dados_extracao[1].text if len(dados_extracao) > 1 else None
        website = validate_website(dados_extracao[2].text) if len(dados_extracao) > 2 else None
        phone = format_phone(dados_extracao[3].text) if len(dados_extracao) > 3 else None
        page_url = driver.current_url

        return {
            "title_maps": nome_empresa,
            "address_maps": address,
            "located_maps": located_in,
            "website_maps": website,
            "phone_maps": phone,
            "page_url_maps": page_url
        }
    except Exception as e:
        with lock:
            logging.error(f"Erro ao extrair dados: {e}")
        return None

def pesquisa_google_maps(termo_pesquisa):
    driver = configurar_driver()
    try:
        driver.get("https://www.google.com/maps")
        search_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
        search_box.send_keys(termo_pesquisa + Keys.RETURN)
        time.sleep(2)
        if acessar_primeiro_resultado(driver):
            return extrair_dados(driver)
    finally:
        driver.quit()
        encerrar_processos_restantes()

def realizar_pesquisas(termos_de_pesquisa):
    resultados = [None] * len(termos_de_pesquisa)  # Preenche a lista para manter a ordem
    with tqdm(total=len(termos_de_pesquisa), desc="Progresso das pesquisas", unit="pesquisa") as pbar:
        threads = []
        for i, termo in enumerate(termos_de_pesquisa):
            thread = threading.Thread(target=pesquisar_termo, args=(termo, i, pbar, resultados))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    return resultados

def pesquisar_termo(termo, index, pbar, resultados):
    with semaforo:
        resultado = pesquisa_google_maps(termo)
        resultados[index] = resultado if resultado else {"title_maps": None, "address_maps": None, "located_maps": None, "website_maps": None, "phone_maps": None, "page_url_maps": None}
        time.sleep(1)
        pbar.update(1)
