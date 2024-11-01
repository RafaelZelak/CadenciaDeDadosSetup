from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from time import sleep
import re
import phonenumbers
import validators

# Configuração do navegador e aplicação do Selenium Stealth
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# Configurando o Selenium Stealth
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
)

# Funções para validar telefone, CEP e website
def format_phone(phone):
    try:
        parsed_phone = phonenumbers.parse(phone, "BR")
        if phonenumbers.is_possible_number(parsed_phone):
            return phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
    except phonenumbers.NumberParseException:
        pass
    return None

def validate_cep(cep):
    return cep if re.match(r"^\d{5}-\d{3}$", cep) else None

def validate_website(url):
    return url if validators.url(url) else "NONE"

# Abrindo o Google Maps e pesquisando o termo desejado
driver.get("https://www.google.com/maps")
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys("CLINICA BIAVATTI CURITIBA")
search_box.send_keys(Keys.RETURN)

# Verifica se há múltiplos resultados e acessa o primeiro resultado não patrocinado
def verificar_e_acessar_primeiro_resultado():
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Nv2PK.Q2HXcd.THOPZb")))
        resultados = driver.find_elements(By.CLASS_NAME, "Nv2PK.Q2HXcd.THOPZb")

        for resultado in resultados:
            if resultado.find_elements(By.XPATH, ".//span[contains(text(), 'Patrocinado')]"):
                continue
            link = resultado.find_element(By.CLASS_NAME, "hfpxzc")
            link.click()
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Io6YTe")))
            return True
        print("Nenhum resultado não patrocinado encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao acessar o primeiro resultado não patrocinado: {e}")
        return False

# Função para extrair e organizar dados da empresa
def extrair_dados():
    try:
        nome_empresa = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob").text

        dados_extracao = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")
        address = dados_extracao[0].text if len(dados_extracao) > 0 else "N/A"
        located_in = dados_extracao[1].text if len(dados_extracao) > 1 else "N/A"
        website = validate_website(dados_extracao[2].text) if len(dados_extracao) > 2 else "NONE"
        phone = format_phone(dados_extracao[3].text) if len(dados_extracao) > 3 else "N/A"

        print(f"Nome da Empresa: {nome_empresa}")
        print(f"Endereço: {address}")
        print(f"Localizado em: {located_in}")
        print(f"Website: {website}")
        print(f"Telefone: {phone}")

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")

# Executa a verificação e acessa o primeiro resultado, se necessário, antes de extrair os dados
if verificar_e_acessar_primeiro_resultado():
    extrair_dados()

# Fecha o navegador
driver.quit()
