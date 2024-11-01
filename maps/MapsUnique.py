from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from time import sleep


# Configuração do navegador e aplicação do Selenium Stealth
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")
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

# Abrindo o Google Maps e pesquisando o termo desejado
driver.get("https://www.google.com/maps")
WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys("Setup Tecnologia Curitiba")
search_box.send_keys(Keys.RETURN)

# Espera os resultados principais aparecerem antes de extrair os dados
WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Io6YTe")))

# Função para extrair dados da empresa
def extrair_dados():
    try:
        address = driver.find_element(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc").text
        located_in = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")[1].text  # Assuming this is always the second element
        website = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")[2].text  # Assuming this is always the third element
        phone = driver.find_elements(By.CLASS_NAME, "Io6YTe.fontBodyMedium.kR99db.fdkmkc")[3].text  # Assuming this is always the fourth element

        print(f"Endereço: {address}")
        print(f"Localizado em: {located_in}")
        print(f"Website: {website}")
        print(f"Telefone: {phone}")

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")

# Executa a função de extração de dados
extrair_dados()

# Fecha o navegador
driver.quit()