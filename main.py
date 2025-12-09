# main.py
import sys
from server_udp import UDPServer
from client_udp import UDPClient

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py [server|client]")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "server":
        server = UDPServer()
        server.run()
    elif mode == "client":
        try:
            porta = int(input("Digite sua porta (ex: 5001, 5002, etc): "))
        except:
            print("❌ Porta inválida")
            exit(1)
        
        client = UDPClient(porta)
        client.run()
    else:
        print("Modo inválido. Use: server ou client")

if __name__ == "__main__":
    main()