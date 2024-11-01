import psycopg2
from flask import session

# Configuração da conexão com o banco de dados
def get_db_connection():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="r1r2r3r4r5",
            host="127.0.0.1",
            port="5432",
            database="EnrichedData"
        )
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para buscar notificações para o usuário logado
def get_user_notifications(username):
    connection = get_db_connection()
    if not connection:
        return []

    notifications = []
    try:
        cursor = connection.cursor()
        # Consulta para buscar o ID do usuário logado
        cursor.execute('SELECT id FROM "Users" WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            # Consulta para buscar as notificações associadas ao usuário
            cursor.execute("""
                SELECT id, enterprise
                FROM "Result"
                WHERE userid = %s AND enviado_bitrix = false
            """, (user_id,))
            results = cursor.fetchall()

            # Debug: Printar os resultados para verificar o que está sendo retornado
            print(f"Resultados da query: {results}")

            # Convertendo os resultados para uma lista de notificações (id, empresa)
            notifications = [{'id': row[0], 'enterprise': row[1]} for row in results]

        cursor.close()
    except Exception as e:
        print(f"Erro ao buscar notificações: {e}")
    finally:
        connection.close()

    # Debug: Printar as notificações para verificação
    print(f"Notificações encontradas: {notifications}")

    return notifications
