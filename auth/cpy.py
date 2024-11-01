import hashlib

def gerar_senha_criptografada(senha):
    # Gera o hash da senha usando SHA-256
    senha_criptografada = hashlib.sha256(senha.encode('utf-8')).hexdigest()
    return senha_criptografada

# Exemplo de uso
senha = input("Digite a senha: ")
senha_criptografada = gerar_senha_criptografada(senha)

print(f"Senha criptografada: {senha_criptografada}")
