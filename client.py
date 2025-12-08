# client.py

import socket
import json

HOST = "127.0.0.1"
PORT = 5000

buffer = ""

def receber(sock):
    global buffer

    try:
        data = sock.recv(4096)
        if not data:
            print("Conexão encerrada pelo servidor.")
            return None

        buffer += data.decode()

    except:
        return None

    if "END" not in buffer:
        return None

    msg, resto = buffer.split("END", 1)
    buffer = resto

    return json.loads(msg.strip())


def enviar(sock, data):
    texto = json.dumps(data) + "\nEND\n"
    sock.sendall(texto.encode())


def main():
    s = socket.socket()
    s.connect((HOST, PORT))
    s.settimeout(30.0)  # Timeout de 30 segundos

    # ============================
    #       FASE DE LOGIN
    # ============================
    tentativas = 0
    while True:
        try:
            data = receber(s)
        except socket.timeout:
            print("Timeout: servidor não respondeu.")
            s.close()
            return

        if data is None:
            continue

        if "msg" in data:
            print(data["msg"])
            
            # Se pedir login, envie comando
            if "login" in data["msg"].lower():
                cmd = input("> ")
                enviar(s, {"cmd": cmd})
            
            # Se login confirmado, aguarde início do jogo
            elif data["msg"] == "você está online!":
                print("Login realizado! Aguardando outros jogadores...")
                # Não quebre o loop ainda
                continue
            
            # Quando receber a mensagem de boas-vindas, saia do loop
            elif "bem-vindo ao jogo" in data.get("msg", "").lower():
                print(data["msg"])
                break
            
            # Outras mensagens
            else:
                print(data["msg"])

        # Se receber mensagem de fim (caso jogo seja cancelado)
        elif data.get("fim"):
            print(data["msg"])
            s.close()
            return

    # ============================
    #      LOOP DO JOGO
    # ============================
    while True:
        try:
            data = receber(s)
        except socket.timeout:
            print("Timeout: servidor não respondeu.")
            break

        if data is None:
            continue

        # fim do jogo
        if data.get("fim"):
            print(data["msg"])
            break

        # turno
        if data.get("turno"):
            print(data["msg"])
            comando = input("> ").strip().lower()
            enviar(s, {"comando": comando})
            continue

        # mensagens comuns
        if "msg" in data:
            print(data["msg"])
            
            # Se for comando inválido, pedir novo comando
            if data["msg"] == "Comando inválido.":
                comando = input("> ").strip().lower()
                enviar(s, {"comando": comando})
    
    s.close()

if __name__ == "__main__":
    main()
