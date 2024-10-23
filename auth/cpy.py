import bcrypt
import getpass  # Para solicitar a senha sem exibi-la no console

def hash_password(password):
    # Gera o hash da senha usando bcrypt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

if __name__ == "__main__":
    # Solicita a senha para criptografar
    senha = getpass.getpass("Digite a senha para criptografar: ")
    senha_criptografada = hash_password(senha)
    print(f"Senha criptografada: {senha_criptografada}")
