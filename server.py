import os
import socket
import json
from game import Game
from player import Player

HOST = "127.0.0.1"
PORT = 5000

# Lista de contatos pré-definida (nome → porta única)
contatos = {
    "Felipe": ("127.0.0.1", 5001),
    "Vitor":  ("127.0.0.1", 5002),
    "Ana":    ("127.0.0.1", 5003),
    "Lucas":  ("127.0.0.1", 5004),
}

# Usuários online (nome já logado)
online = {}

def enviar(conn, data):
    texto = json.dumps(data) + "\nEND\n"
    conn.sendall(texto.encode())


buffers = {}  # buffer individual de cada cliente

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


def realizar_login(conn):
    """
    Mantém o cliente preso até fazer login correto.
    Retorna o nome do usuário autenticado.
    """
    enviar(conn, {"msg": "Digite: login <nome>"})

    while True:
        data = receber(conn)
        if not data:
            return None
        
        comando = data.get("cmd", "")
        partes = comando.split()

        if len(partes) == 0:
            enviar(conn, {"msg": "Digite: login <nome>"})
            continue

        if partes[0] != "login":
            enviar(conn, {"msg": "Comando inválido. Use: login <nome>"})
            continue

        if len(partes) < 2:
            enviar(conn, {"msg": "Formato correto: login <nome>"})
            continue

        nome = partes[1]

        # verificar se nome existe na lista de contatos
        if nome not in contatos:
            enviar(conn, {"msg": "Usuário não existe na lista de contatos!"})
            continue

        # verificar se já está online
        if nome in online:
            enviar(conn, {"msg": "Esse usuário já está online!"})
            continue

        # LOGIN OK
        online[nome] = contatos[nome]
        enviar(conn, {"msg": "você está online!"})
        print(f"[LOGIN] {nome} conectou-se.")
        return nome


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print("Servidor iniciado. Aguardando jogadores...")

    game = Game()

    # ============================
    #        FASE DE LOGIN
    # ============================
    while len(game.jogadores) < 2:
        conn, addr = s.accept()

        nome = realizar_login(conn)
        if nome is None:
            conn.close()
            continue

        pid = len(game.jogadores)
        p = Player(pid, conn, addr, nome=nome)
        game.add_player(p)

        enviar(conn, {"msg": f"Bem-vindo ao jogo, {nome}! (Jogador {pid})"})

    print("Iniciando jogo...")

    # ============================
    #        LOOP DO JOGO
    # ============================
    fim = False
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        print("Mapa atual:")
        mapa = game.gerar_mapa()
        for linha in mapa:
            print(linha)
        
        if fim:
            break

        # Detectar jogadores juntos
        posicoes = {}
        for p in game.jogadores:
            x, y = p.pos
            if (x, y) in posicoes:
                outro = posicoes[(x, y)]
                print(f"\nJogador {outro.pid} ({outro.nome}) e Jogador {p.pid} ({p.nome}) "
                      f"estão na mesma posição ({x},{y})")
            else:
                posicoes[(x, y)] = p

        print("\n--- RODADA NOVA ---")

        comandos = {}

        # solicitar comandos
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
            comando = comandos[p.pid]
            achou, msg = game.comando(p, comando)
            enviar(p.conn, {"msg": msg})

            if achou:
                for outro in game.jogadores:
                    enviar(outro.conn, {"fim": True,
                        "msg": f"Jogador {p.pid} ({p.nome}) encontrou o tesouro!"})
                fim = True
                break

    s.close()


if __name__ == "__main__":
    main()
