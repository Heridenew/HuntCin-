import os
import time

def abrir_terminal(comando):
    """
    Abre um novo terminal no Windows e executa o comando.
    """
    os.system(f'start cmd /k "{comando}"')


def main():
    # Caminhos dos scripts
    server = "python server.py"
    client = "python client.py"

    print("Iniciando servidor...")
    abrir_terminal(server)

    # Pequeno delay para o servidor subir
    time.sleep(1)

    print("Iniciando Cliente 1...")
    abrir_terminal(client)

    # Mais um pequeno delay
    time.sleep(1)

    print("Iniciando Cliente 2...")
    abrir_terminal(client)

    print("Ambiente de teste iniciado com sucesso!")


if __name__ == "__main__":
    main()
