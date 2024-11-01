import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

# Pegar as credenciais do ambiente
server_ip = os.getenv('SERVER_IP')
username = os.getenv('SERVER_LOGIN')
password = os.getenv('SERVER_PASSWORD')

# Palavras que identificam o início e o fim de um bloco de login
login_start_keywords = ["DN:", "cn:"]
login_end_keywords = ["homePhone:"]  # Palavras que indicam o final de um bloco de login

def is_login_start(line):
    return any(keyword in line for keyword in login_start_keywords)

def is_login_end(line):
    return any(keyword in line for keyword in login_end_keywords)

def format_datetime_header(datetime_str):
    return f"\n{'-'*10} {datetime_str.center(30)} {'-'*10}\n"

def remove_datetime_from_line(line):
    return ": ".join(line.split(": ")[1:]) if ": " in line else line

def get_login_logs():
    if server_ip and username and password:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(server_ip, username=username, password=password)
            command = 'cat /var/log/gunicorn/gunicorn.log'
            stdin, stdout, stderr = ssh.exec_command(command)

            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            if error:
                print(f"Erro ao executar comando: {error}")
                return []

            capturing_login = False
            login_block = []
            all_logins = []
            current_datetime = ""

            for line in output.splitlines():
                if is_login_start(line):
                    current_datetime = " ".join(line.split()[0:3])
                    capturing_login = True
                    login_block = [remove_datetime_from_line(line)]
                elif capturing_login:
                    login_block.append(remove_datetime_from_line(line))
                    if is_login_end(line):
                        formatted_login = format_datetime_header(current_datetime) + "\n".join(login_block)
                        all_logins.append(formatted_login)
                        capturing_login = False

            return all_logins if all_logins else ["Nenhum login encontrado."]

        finally:
            ssh.close()
    else:
        print("As credenciais não foram carregadas corretamente.")
        return []  # Retorna uma lista vazia se houver erro nas credenciais

