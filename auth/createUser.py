import psycopg2
import bcrypt
import getpass  # Para solicitar a senha sem exibi-la no console

def hash_password(password):
    # Gera o hash da senha usando bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_user():
    # Solicita os dados no console
    username = input("Digite o nome de usuário: ")
    email = input("Digite o e-mail: ")
    full_name = input("Digite o nome completo: ")
    password = getpass.getpass("Digite a senha: ")

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

        # Verifica se o usuário já existe
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("Usuário já existe. Escolha outro nome de usuário.")
            return

        # Gera o hash da senha
        hashed_password = hash_password(password)

        # Insere o novo usuário no banco de dados
        insert_query = """
        INSERT INTO users (username, password, email, full_name)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (username, hashed_password, email, full_name))

        # Confirma a inserção
        connection.commit()

        print(f"Usuário '{username}' criado com sucesso!")

    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_user()
