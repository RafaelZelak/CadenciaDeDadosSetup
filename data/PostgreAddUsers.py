import psycopg2
from ldap3 import Connection, Server, ALL_ATTRIBUTES, SUBTREE

# Função para verificar e inserir usernames na tabela Users
def insert_usernames(usernames):
    connection = None
    try:
        # Conectando à base de dados "EnrichedData"
        connection = psycopg2.connect(user="postgres", password="r1r2r3r4r5", host="127.0.0.1", port="5432", database="EnrichedData")
        cursor = connection.cursor()

        # Verificar usernames já existentes no banco de dados
        cursor.execute('SELECT username FROM "Users";')
        existing_usernames = {row[0] for row in cursor.fetchall()}

        # Filtrar usernames que ainda não estão no banco
        new_usernames = [username for username in usernames if username not in existing_usernames]

        if new_usernames:
            # Inserindo os novos usernames na tabela Users
            insert_query = 'INSERT INTO "Users" (username) VALUES (%s);'
            usernames_utf8 = [(username.encode('utf-8').decode('utf-8'),) for username in new_usernames]

            cursor.executemany(insert_query, usernames_utf8)
            connection.commit()

            print(f"{cursor.rowcount} novos usernames inseridos na tabela 'Users' com sucesso!")
        else:
            print("Nenhum username novo para inserir.")

    except psycopg2.Error as db_error:
        print(f"Erro de banco de dados: {db_error}")
    except UnicodeDecodeError as decode_error:
        print(f"Erro de codificação UTF-8: {decode_error}")
    except Exception as error:
        print(f"Erro ao inserir os usernames: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Função para buscar usernames no LDAP
def fetch_usernames_from_ldap():
    try:
        server = Server('digitalup.intranet', get_info=ALL_ATTRIBUTES)
        con = Connection(server, user='administrator@digitalup.intranet', password='&ajhsRlm88s!@SF', auto_bind=True)

        search_base = 'DC=digitalup,DC=intranet'
        search_filter = '(objectClass=user)'  # Buscar diretamente os usuários
        attributes = ['sAMAccountName']  # Atributo de username

        con.search(search_base, search_filter, attributes=attributes, search_scope=SUBTREE)

        # Filtrar usernames que não terminam com "$"
        usernames_list = [str(entry.sAMAccountName) for entry in con.entries if not str(entry.sAMAccountName).endswith('$')]

        print(f"Usernames encontrados no LDAP: {usernames_list}")
        return usernames_list

    except Exception as e:
        print(f"Ocorreu um erro durante a busca no LDAP: {e}")
        return []

# Função principal para buscar do LDAP e inserir no PostgreSQL
def main():
    usernames = fetch_usernames_from_ldap()
    if usernames:
        insert_usernames(usernames)

if __name__ == "__main__":
    main()
