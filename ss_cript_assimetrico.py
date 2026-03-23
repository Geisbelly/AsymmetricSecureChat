import random
from math import gcd
import hashlib

# ===== RSA BASE =====

def eh_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def gerar_primo():
    while True:
        n = random.randint(100, 300)
        if eh_primo(n):
            return n


def inverso_modular(e, phi):
    for d in range(1, phi):
        if (e * d) % phi == 1:
            return d


def gerar_chaves():
    p = gerar_primo()
    q = gerar_primo()
    while p == q:
        q = gerar_primo()

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 3
    while gcd(e, phi) != 1:
        e += 2

    d = inverso_modular(e, phi)

    return (e, n), (d, n)


# ===== SEGURANÇA =====

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# ===== USUÁRIO =====

class Usuario:
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha_hash = hash_senha(senha)
        self.publica, self.privada = gerar_chaves()
        self.caixa_entrada = []

        print(f"\n💻 [{nome}] criado!")

    def verificar_senha(self, senha):
        return self.senha_hash == hash_senha(senha)

    def hash_msg(self, msg):
        return sum(ord(c) for c in msg) % 1000

    def assinar(self, msg):
        print(f"\n💻 [{self.nome}] ASSINANDO")
        h = self.hash_msg(msg)
        print("Hash:", h)

        d, n = self.privada
        assinatura = pow(h, d, n)

        print("Assinatura:", assinatura)
        return assinatura


# ===== CRIPTO =====

def criptografar(msg, chave_publica):
    print("\n🔐 CRIPTOGRAFANDO")
    e, n = chave_publica
    ascii_vals = [ord(c) for c in msg]
    print("ASCII:", ascii_vals)

    cripto = [pow(v, e, n) for v in ascii_vals]
    print("Criptografado:", cripto)

    return cripto


def descriptografar(msg_cripto, chave_privada):
    print("\n🔓 DESCRIPTOGRAFANDO")
    d, n = chave_privada

    valores = [pow(c, d, n) for c in msg_cripto]
    print("Valores:", valores)

    try:
        texto = "".join(chr(v) for v in valores)
    except:
        texto = "[ERRO AO CONVERTER]"

    print("Mensagem:", texto)
    return texto


# ===== MENSAGEM =====

class Mensagem:
    def __init__(self, autor, conteudo, assinatura):
        self.autor = autor
        self.conteudo = conteudo
        self.assinatura = assinatura


# ===== SISTEMA =====

usuarios = {}
usuario_logado = None


# ===== LOGIN =====

def login():
    global usuario_logado

    nome = input("Usuário: ")

    if nome not in usuarios:
        print("Novo usuário, crie uma senha")
        senha = input("Senha: ")
        usuarios[nome] = Usuario(nome, senha)
        usuario_logado = usuarios[nome]
        return

    senha = input("Senha: ")

    if usuarios[nome].verificar_senha(senha):
        usuario_logado = usuarios[nome]
        print(f"\n✔ Bem-vindo, {nome}")
    else:
        print("❌ Senha incorreta")


# ===== ENVIO =====

def enviar_mensagem():
    if not usuario_logado:
        print("Faça login primeiro!")
        return

    destino_nome = input("Enviar para: ")

    if destino_nome not in usuarios:
        print("Usuário não existe. Criando...")
        senha = input(f"Defina uma senha para {destino_nome}: ")
        usuarios[destino_nome] = Usuario(destino_nome, senha)

    destino = usuarios[destino_nome]
    texto = input("Mensagem: ")

    print("\n💻", usuario_logado.nome, "──▶ 💻", destino.nome)

    print("\n--- ASSINATURA ---")
    assinatura = usuario_logado.assinar(texto)

    print("\n--- CRIPTOGRAFIA ---")
    cripto = criptografar(texto, destino.publica)

    msg = Mensagem(usuario_logado.nome, cripto, assinatura)
    destino.caixa_entrada.append(msg)

    print("\n📦 Mensagem enviada!")


# ===== CAIXA =====

def ver_caixa():
    if not usuario_logado:
        print("Faça login primeiro!")
        return

    inbox = usuario_logado.caixa_entrada

    if not inbox:
        print("Caixa vazia")
        return

    print("\n=== CAIXA DE ENTRADA ===")
    for i, msg in enumerate(inbox):
        print(f"{i} - De: {msg.autor}")

    try:
        idx = int(input("Escolha: "))
        msg = inbox[idx]
    except:
        print("Entrada inválida")
        return

    print("\n💻", usuario_logado.nome, "(abrindo mensagem)")

    print("\n--- DESCRIPTOGRAFAR ---")
    texto = descriptografar(msg.conteudo, usuario_logado.privada)

    print("\n--- VERIFICAR ASSINATURA ---")
    autor = usuarios[msg.autor]

    h = sum(ord(c) for c in texto) % 1000
    print("Hash calculado:", h)

    e, n = autor.publica
    h_assinado = pow(msg.assinatura, e, n)

    print("Hash assinatura:", h_assinado)

    if h == h_assinado:
        print("✔ Assinatura válida!")
    else:
        print("❌ Assinatura inválida!")


# ===== ESPIONAGEM =====

def espionar_mensagem():
    if not usuario_logado:
        print("Faça login primeiro!")
        return

    print("\n=== USUÁRIOS ===")
    nomes = list(usuarios.keys())

    for i, nome in enumerate(nomes):
        print(f"{i} - {nome}")

    try:
        idx = int(input("Escolha usuário: "))
        alvo = usuarios[nomes[idx]]
    except:
        print("Erro")
        return

    if not alvo.caixa_entrada:
        print("Sem mensagens")
        return

    print("\n=== MENSAGENS DO ALVO ===")
    for i, msg in enumerate(alvo.caixa_entrada):
        print(f"{i} - De: {msg.autor}")

    try:
        idx = int(input("Escolha mensagem: "))
        msg = alvo.caixa_entrada[idx]
    except:
        print("Erro")
        return

    print("\n💀 ESPIONANDO (SEM CHAVE CORRETA) 💀")

    texto = descriptografar(msg.conteudo, usuario_logado.privada)

    print("\n🔍 Verificando assinatura...")

    autor = usuarios[msg.autor]

    h = sum(ord(c) for c in texto) % 1000
    e, n = autor.publica
    h_assinado = pow(msg.assinatura, e, n)

    print("Hash calculado:", h)
    print("Hash assinatura:", h_assinado)

    if h == h_assinado:
        print("⚠️ Estranho... não deveria funcionar. Você tá se espionando? ⚠️")
    else:
        print("✔ Falha (como esperado)")


# ===== TESTE =====

def teste():
    print("\n=== TESTE AUTOMÁTICO ===")

    a = Usuario("Alice", "123")
    b = Usuario("Bob", "123")

    msg = "mensagem secreta"

    print("\n💻 Alice → 💻 Bob")

    assinatura = a.assinar(msg)
    cripto = criptografar(msg, b.publica)

    mensagem = Mensagem("Alice", cripto, assinatura)

    print("\n💻 Bob recebendo...")

    texto = descriptografar(mensagem.conteudo, b.privada)

    h = sum(ord(c) for c in texto) % 1000
    e, n = a.publica
    h_assinado = pow(mensagem.assinatura, e, n)

    print("✔ OK" if h == h_assinado else "❌ ERRO")


# ===== MAIN =====

def main():
    while True:
        print("\n=== SISTEMA CRIPTOGRÁFICO ===")
        print("1 - Login")
        print("2 - Enviar mensagem")
        print("3 - Caixa de entrada")
        print("4 - Espionar (ataque)")
        print("5 - Teste automático")
        print("0 - Sair")

        op = input("Escolha: ")

        if op == "1":
            login()
        elif op == "2":
            enviar_mensagem()
        elif op == "3":
            ver_caixa()
        elif op == "4":
            espionar_mensagem()
        elif op == "5":
            teste()
        elif op == "0":
            break
        else:
            print("Opção inválida")


if __name__ == "__main__":
    main()