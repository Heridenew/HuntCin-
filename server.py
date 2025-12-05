import os
import socket
import json
import threading
from game import Game
from player import Player

HOST = "127.0.0.1"
PORT = 5000

CONTATOS_FILE = "contatos.txt"

online = {}
buffers = {}
contatos = {}   # será carregado do arquivo


# ==============================
# UTILITÁRIOS
# ==============================

def carregar_contatos():
    global contatos
    contatos.clear()

    if not os.path.exists(CONTATOS_FILE):
        return

    with open(CONTATOS_FILE, "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue

            nome, ipporta = linha.split(";")
            ip, porta = ipporta.split(":")
            contatos[nome] = (ip, int(porta))


def salvar_contatos():
    with open(CONTATOS_FILE, "w") as f:
        for nome, (ip, porta) in contatos.items():
            f.write(f"{nome};{ip}:{porta}\n")


def enviar(conn, data):
    texto = json.dumps(data) + "\nEND\n"
    conn.sendall(texto.encode())


def receber(conn):
    if conn not in buffers:
        buffers[conn] = ""

    try:
        buffers[conn] += conn.recv(4096).decode()
    except:
        return None

    if "END" not in buffers[conn]:
        return None

    msg, resto = buffers[conn].split("END", 1)
    buffers[conn] = resto
    return json.loads(msg.strip())

def porta_em_uso(porta):
    # verifica nas contas já cadastradas
    for _, (_, porta_existente) in contatos.items():
        if porta_existente == porta:
            return True

    # verifica usuários online
    for _, (_, porta_existente) in online.items():
        if porta_existente == porta:
            return True

    return False


def encerrar_por_logout(game, jogador_desconectado):
    nome = jogador_desconectado.nome

    # achar o outro jogador
    for p in game.jogadores:
        if p != jogador_desconectado:
            outro = p
            break
    else:
        return  # só 1 jogador? não faz nada

    # manda mensagens finais
    enviar(outro.conn, {
        "fim": True,
        "msg": f"O jogador {nome} fez LOGOUT. Você venceu!"
    })

    enviar(jogador_desconectado.conn, {
        "fim": True,
        "msg": "Você saiu do jogo (LOGOUT)."
    })

    try:
        outro.conn.close()
    except:
        pass

    try:
        jogador_desconectado.conn.close()
    except:
        pass


# ==============================
# LOGIN
# ==============================

def realizar_login(conn):
    enviar(conn, {"msg": "Digite: login <nome>"})

    while True:
        data = receber(conn)

        # Nada recebido → manda instrução novamente
        if data is None:
            enviar(conn, {"msg": "Digite: login <nome>"})
            continue

        cmd = data.get("cmd")
        if not cmd:
            enviar(conn, {"msg": "Digite: login <nome>"})
            continue

        partes = cmd.split()

        if len(partes) != 2 or partes[0] != "login":
            enviar(conn, {"msg": "Comando inválido. Use: login <nome>"})
            continue

        nome = partes[1]

        if nome not in contatos:
            enviar(conn, {"msg": "Usuário não existe na lista de contatos!"})
            continue

        if nome in online:
            enviar(conn, {"msg": "Esse usuário já está online!"})
            continue

        # LOGIN OK
        online[nome] = contatos[nome]
        enviar(conn, {"msg": "você está online!"})
        print(f"[LOGIN] {nome} entrou no sistema.")
        return nome


# ==============================
# THREAD DO LOGIN
# ==============================

class LoginThread(threading.Thread):
    def __init__(self, conn, addr, game):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.game = game

    def run(self):
        nome = realizar_login(self.conn)
        if not nome:
            self.conn.close()
            return

        pid = len(self.game.jogadores)
        p = Player(pid, self.conn, self.addr, nome=nome)
        self.game.add_player(p)

        enviar(self.conn, {"msg": f"Bem-vindo ao jogo, {nome}! (Jogador {pid+1})"})
        print(f"[JOGO] Jogador {pid+1} ({nome}) conectado.")


# ==============================
# MENU DO SERVIDOR
# ==============================

def menu():
    carregar_contatos()

    while True:
        print("\n============================")
        print("          MENU")
        print("============================")
        print("1) Iniciar jogo")
        print("2) Permitir cadastro")
        print("3) Quit")
        print("============================")

        op = input("> ").strip()

        if op == "1":
            return "start"

        elif op == "2":
            nome = input("Nome do novo usuário: ").strip()
            ipporta = input("Digite IP:PORTA (ex: 192.168.100.100:5000): ").strip()

            if nome in contatos:
                print("Esse nome já existe!")
                continue

            try:
                ip, porta_str = ipporta.split(":")
                porta = int(porta_str)
            except:
                print("Formato inválido. Use IP:PORTA")
                continue

            # 🔥 verificação de porta duplicada
            if porta_em_uso(porta):
                print(f"A porta {porta} já está em uso! Escolha outra.")
                continue

            contatos[nome] = (ip, porta)
            salvar_contatos()

            print("Usuário cadastrado e salvo!")


        elif op == "3":
            exit(0)

        else:
            print("Opção inválida.")


# ==============================
# MAIN DO SERVIDOR
# ==============================

def main():
    if menu() != "start":
        return

    carregar_contatos()

    total_jogadores = int(input("Quantos jogadores irão jogar? "))

    # 🌟 ABRIR AUTOMATICAMENTE CLIENTS 🌟
    for i in range(total_jogadores):
        os.system("start cmd /k python client.py")

    game = Game()

    # socket servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print("\nServidor iniciado. Aguardando jogadores...")

    while len(game.jogadores) < total_jogadores:
        conn, addr = s.accept()
        print(f"[CONEXÃO] Nova conexão: {addr}")

        th = LoginThread(conn, addr, game)
        th.start()

    print("\n>>> Todos os jogadores conectados! Iniciando jogo...\n")

    # ---------- LOOP DO JOGO ----------
    fim = False
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        print("Mapa atual:")
        for linha in game.gerar_mapa():
            print(linha)

        if fim:
            break

        print("\n--- RODADA NOVA ---")
        comandos = {}

        for p in game.jogadores:
            enviar(p.conn, {"turno": True, "msg": "Digite seu comando:"})

        # receber comandos
        for p in game.jogadores:
            data = None
            while data is None:
                data = receber(p.conn)
            comandos[p.pid] = data["comando"]

        # processar comandos
        for p in game.jogadores:
            cmd = comandos[p.pid]

        # ----------------------------
        #   VERIFICAR LOGOUT
        # ----------------------------
        if cmd.lower() == "logout":
            print(f"[LOGOUT] {p.nome} saiu do jogo.")
            encerrar_por_logout(game, p)
            fim = True
            break

        # ----------------------------
        #   PROCESSAR COMANDO NORMAL
        # ----------------------------
        achou, msg = game.comando(p, cmd)
        enviar(p.conn, {"msg": msg})

        if achou:
            for o in game.jogadores:
                enviar(o.conn, {
                    "fim": True,
                    "msg": f"Jogador {p.pid+1} ({p.nome}) encontrou o tesouro!"
                })
            fim = True
            break


    s.close()


if __name__ == "__main__":
    main()
