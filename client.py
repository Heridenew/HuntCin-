# client.py

import socket
import json

HOST = "127.0.0.1"
PORT = 5000

buffer = ""

def receber(sock):
    global buffer

    try:
        buffer += sock.recv(4096).decode()
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

    # ============================
    #       FASE DE LOGIN
    # ============================
    while True:
        data = receber(s)
        if data is None:
            continue

        # servidor pede login
        if "msg" in data:
            print(data["msg"])

        # cliente responde com o comando login
        if "Digite:" in data["msg"] or "login" in data["msg"]:
            cmd = input("> ")
            enviar(s, {"cmd": cmd})
            continue

        # login aceito
        if data.get("msg") == "você está online!":
            print("Login realizado com sucesso!")
            break

    # ============================
    #      LOOP DO JOGO
    # ============================
    while True:
        data = receber(s)
        if data is None:
            continue

        # fim do jogo
        if "fim" in data:
            print(data["msg"])
            break

        # turno
        if "turno" in data:
            print(data["msg"])
            comando = input("> ").strip().lower()
            enviar(s, {"comando": comando})
            continue

        # mensagens comuns
        if "msg" in data:
            print(data["msg"])

        # estado opcional
        if "estado" in data:
            print("\nEstado:", data["estado"])

    s.close()


if __name__ == "__main__":
    main()
