import os
import socket
import json
import threading
import time
from game import Game
from player import Player

HOST = "127.0.0.1"
PORT = 5000

CONTATOS_FILE = "contatos.txt"

online = {}
buffers = {}
contatos = {}   # será carregado do arquivo

# ==============================
#         UTILITÁRIOS
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
        data_raw = conn.recv(4096)
        if not data_raw:
            return {"desconectou": True}
        buffers[conn] += data_raw.decode()

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

    outro = None
    for p in game.jogadores:
        if p != jogador_desconectado:
            outro = p
            break

    # jogador sozinho no jogo
    if outro is None:
        try:
            enviar(jogador_desconectado.conn, {
                "fim": True,
                "msg": "Você saiu do jogo (LOGOUT)."
            })
        except:
            pass
        return

    # avisar o outro jogador
    try:
        enviar(outro.conn, {
            "fim": True,
            "msg": f"O jogador {nome} fez LOGOUT. Você venceu!"
        })
    except:
        pass

    # avisar o que saiu
    try:
        enviar(jogador_desconectado.conn, {
            "fim": True,
            "msg": "Você saiu do jogo (LOGOUT)."
        })
    except:
        pass

# ==============================
#            LOGIN
# ==============================

def realizar_login(conn):
    enviar(conn, {"msg": "Digite: login <nome>"})
    
    tentativas = 0
    while tentativas < 3:  # Limite de tentativas
        data = receber(conn)
        if data is None:
            continue
        
        if "cmd" in data:
            comando = data["cmd"].strip()
            
            if comando.lower().startswith("login "):
                nome = comando[6:].strip()
                
                if nome in contatos:
                    if nome in online:
                        enviar(conn, {"msg": f"Usuário {nome} já está online."})
                        tentativas += 1
                        if tentativas < 3:
                            enviar(conn, {"msg": "Digite: login <nome>"})
                        continue
                    
                    # Login bem-sucedido
                    online[nome] = conn.getpeername()
                    enviar(conn, {"msg": "você está online!"})
                    return nome
                else:
                    enviar(conn, {"msg": f"Nome '{nome}' não cadastrado."})
                    tentativas += 1
                    if tentativas < 3:
                        enviar(conn, {"msg": "Digite: login <nome>"})
            else:
                enviar(conn, {"msg": "Comando inválido. Use: login <nome>"})
                tentativas += 1
                if tentativas < 3:
                    enviar(conn, {"msg": "Digite: login <nome>"})
    
    # Tentativas esgotadas
    enviar(conn, {"msg": "Número máximo de tentativas excedido."})
    return None


# ==============================
#        THREAD DO LOGIN
# ==============================

class LoginThread(threading.Thread):
    def __init__(self, conn, addr, game):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.game = game
        self.nome = None

    def run(self):
        self.nome = realizar_login(self.conn)
        
        if self.nome:
            pid = len(self.game.jogadores)
            p = Player(pid, self.conn, self.addr, nome=self.nome)
            self.game.add_player(p)
            
            enviar(self.conn, {"msg": f"Bem-vindo ao jogo, {self.nome}! (Jogador {pid+1})"})
            print(f"[JOGO] Jogador {pid+1} ({self.nome}) conectado.")
        else:
            try:
                self.conn.close()
            except:
                pass
# ==============================
#       MENU DO SERVIDOR
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
#       MAIN DO SERVIDOR
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

    login_threads = []
    connections = []

    # PRIMEIRO: Aceitar TODAS as conexões
    while len(connections) < total_jogadores:
        conn, addr = s.accept()
        print(f"[CONEXÃO] Nova conexão: {addr}")
        connections.append((conn, addr))

    # SEGUNDO: Iniciar threads de login para TODAS as conexões
    for conn, addr in connections:
        th = LoginThread(conn, addr, game)
        th.start()
        login_threads.append(th)

    # TERCEIRO: Aguardar todas as threads terminarem
    for th in login_threads:
        th.join()

    # ==========================================
    # VERIFICAÇÃO DE LOGINS BEM-SUCEDIDOS
    # ==========================================
    login_threads_sucesso = [th for th in login_threads if th.nome is not None]
    jogadores_conectados = len(login_threads_sucesso)

    print(f"\n>>> {jogadores_conectados} de {total_jogadores} jogadores conectados")

    if jogadores_conectados < total_jogadores:
        print("Não há jogadores suficientes. Encerrando...")
        # Fechar conexões restantes
        for th in login_threads:
            if th.nome:
                try:
                    enviar(th.conn, {"fim": True, "msg": "Jogo cancelado - jogadores insuficientes."})
                    th.conn.close()
                except:
                    pass
            else:
                try:
                    th.conn.close()
                except:
                    pass
        s.close()
        return

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

        for p in game.jogadores:
            enviar(p.conn, {"turno": True, "msg": "Digite seu comando:"})

        # ----------------------------
        #   RECEBER E PROCESSAR COMANDOS
        # ----------------------------
        for p in game.jogadores:
            data = receber(p.conn)

            # jogador caiu ou desconectou
            if not data or "desconectou" in data:
                print(f"[DESCONECTADO] {p.nome} saiu do jogo.")
                encerrar_por_logout(game, p)
                fim = True
                break

            cmd = data.get("comando", "").lower()

            # ----------- LOGOUT ----------
            if cmd == "logout":
                print(f"[LOGOUT] {p.nome} saiu do jogo.")
                encerrar_por_logout(game, p)
                fim = True
                break

            # --------- COMANDO NORMAL ---------
            achou, msg = game.comando(p, cmd)
            enviar(p.conn, {"msg": msg})

            # jogador ganhou
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