import psycopg2
from flask import session
from ldap3 import Server, Connection, ALL_ATTRIBUTES

# Função principal de autenticação
def authenticate(username, password):
    # Tenta autenticar pelo AD primeiro
    if authenticate_ad(username, password):
        return True
    # Se falhar, tenta pelo banco de dados
    elif authenticate_db(username, password):
        return True
    else:
        return False

# Função de autenticação pelo AD
def authenticate_ad(username, password):
    domain = 'digitalup.intranet'
    server = Server(domain, get_info=ALL_ATTRIBUTES)
    user = f'{username}@{domain}'
    conn = Connection(server, user=user, password=password)

    try:
        if conn.bind():
            # Pesquisa pelo usuário no LDAP
            conn.search(
                search_base='DC=digitalup,DC=intranet',
                search_filter=f'(sAMAccountName={username})',
                attributes=['cn', 'memberOf', 'homePhone', 'telephoneNumber']
            )

            if len(conn.entries) > 0:
                user_info = conn.entries[0]
                full_name = user_info.cn.value if hasattr(user_info, 'cn') else None
                is_admin = False

                # Verifica se o usuário pertence ao grupo de Administradores
                if hasattr(user_info, 'memberOf'):
                    for group in user_info.memberOf:
                        if 'CN=Administrators' in group:
                            is_admin = True
                            break

                # Armazena as informações na sessão
                session['logged_in'] = True
                session['username'] = username
                session['full_name'] = full_name
                session['is_admin'] = is_admin

                return True
        return False
    except Exception as e:
        print(f"Erro de autenticação LDAP: {e}")
        return False
    finally:
        conn.unbind()

# Função de autenticação pelo banco de dados
def authenticate_db(username, password):
    try:
        # Conecta ao banco de dados PostgreSQL
        connection = psycopg2.connect(
            user="postgres",
            password="r1r2r3r4r5",
            host="127.0.0.1",
            port="5432",
            database="LeadGenerator"
        )
        cursor = connection.cursor()

        # Consulta para verificar se o usuário existe e obter a senha
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]  # Senha armazenada no banco

            # Verifica se a senha fornecida é igual à senha armazenada
            if password == stored_password:
                # Se a senha for válida, armazena as informações na sessão
                session['logged_in'] = True
                session['username'] = username
                session['full_name'] = username

                return True
            else:
                print("Senha inválida")
                return False  # Senha não corresponde
        else:
            print("Usuário não encontrado")
            return False  # Usuário não encontrado

    except Exception as e:
        print(f"Erro de autenticação no banco de dados: {e}")
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()
