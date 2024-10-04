# CadenciaDeDadosSetup

O **CadenciaDeDadosSetup** é uma ferramenta projetada para enriquecer dados de CNPJs obtidos a partir da API da Receita (Casa de Dados). A partir desses dados, você pode enviá-los para o Bitrix ou gerar planilhas. O enriquecimento dos dados é feito através de um web scraping simples utilizando a biblioteca Beautiful Soup, focado no Knowledge Graph do Google. Além disso, há uma integração com Selenium para um enriquecimento mais refinado.

## Funcionalidades

- **Busca de CNPJs:** Realiza a procura de CNPJs utilizando a API da Receita.
- **Envio para Bitrix ou Geração de Planilhas:** Os dados podem ser enviados para o Bitrix ou gerados como planilhas.
- **Web Scraping:** Os dados enviados para o Bitrix são enriquecidos via web scraping com Beautiful Soup.
- **Armazenamento de Dados:** Dados fracos são armazenados em um datasheet, que pode ser processado com o script `data/RunScrap.py`, onde os dados são enriquecidos usando Selenium.
- **Banco de Dados:** Os dados enriquecidos são armazenados em um banco de dados PostgreSQL.
- **Exibição de Dados:** Os dados estão disponíveis para os usuários no próximo login.
- **Login Baseado em LDAP Active Directory:** Implementação de autenticação via LDAP para controle de acesso.

## Configuração
Mudanças Necessárias
Antes de executar o projeto, você precisará realizar as seguintes modificações:

### Configurar o Domínio LDAP:

Altere o domínio no seguinte trecho de código para o seu próprio domínio LDAP:

````python
def authenticate(username, password):
    domain = 'digitalup.intranet'  # Altere para o seu domínio
    server = Server(domain, get_info=ALL_ATTRIBUTES)
    user = f'{username}@{domain}'
    conn = Connection(server, user=user, password=password)
````

### Atualizar a API do Bitrix:

Altere a URL da API do Bitrix para corresponder à sua configuração:

````python
lead_link = f"https://setup.bitrix24.com.br/crm/lead/show/{lead_id}/"  # Altere conforme necessário
````

### Alterar Credenciais do Banco de Dados:

Atualize as credenciais de conexão com o banco de dados PostgreSQL:
````python
return psycopg2.connect(
    user="postgres",           # Nome de usuário
    password="r1r2r3r4r5",    # Senha
    host="127.0.0.1",         # Endereço do host
    port="5432",              # Porta
    database="EnrichedData"   # Nome do banco de dados
)
````

## Como Usar
### Clone este repositório:
````bash
git clone https://github.com/RafaelZelak/CadenciaDeDadosSetup.git
````

### Instale as dependências necessárias:
(Com o seu venv já criado)

````bash
pip install -r requirements.txt
````


