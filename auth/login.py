import psycopg2
from flask import session

def authenticate(username, password):
    # Autenticação diretamente no banco de dados PostgreSQL
    return authenticate_db(username, password)

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
                session['full_name'] = username  # Pode ser substituído por outro dado, se houver

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
