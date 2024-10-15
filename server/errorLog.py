import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

# Pegar as credenciais do ambiente
server_ip = os.getenv('SERVER_IP')
username = os.getenv('SERVER_LOGIN')
password = os.getenv('SERVER_PASSWORD')

# Palavras que identificam o início e o fim de um bloco de erro
error_start = "Traceback (most recent call last):"
error_end_keywords = ["SystemExit", "sys.exit", "KeyboardInterrupt"]

def is_error_end(line):
    return any(keyword in line for keyword in error_end_keywords)

def format_datetime_header(datetime_str):
    return f"\n{'-'*10} {datetime_str.center(30)} {'-'*10}\n"

def remove_datetime_from_line(line):
    return ": ".join(line.split(": ")[1:]) if ": " in line else line

def get_error_logs():
    if server_ip and username and password:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(server_ip, username=username, password=password)
            command = 'cat /var/log/gunicorn/gunicorn.log'
            stdin, stdout, stderr = ssh.exec_command(command)

            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            capturing_error = False
            error_block = []
            all_errors = []
            current_datetime = ""

            for line in output.splitlines():
                if error_start in line:
                    current_datetime = " ".join(line.split()[0:3])  # Ex: "Oct 07 16:00:14"
                    capturing_error = True
                    error_block = [remove_datetime_from_line(line)]
                elif capturing_error:
                    error_block.append(remove_datetime_from_line(line))
                    if is_error_end(line):
                        formatted_error = format_datetime_header(current_datetime) + "\n".join(error_block)
                        all_errors.append(formatted_error)
                        capturing_error = False

            return all_errors if all_errors else ["Nenhum erro encontrado no log."]
        finally:
            ssh.close()
    else:
        return ["As credenciais não foram carregadas corretamente."]