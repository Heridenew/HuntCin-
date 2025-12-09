# client_udp.py
import socket
import time
from network.rdt import RDT
from utils.config import SERVER_HOST, SERVER_PORT
from network.rdt import RDT
from utils.config import Config

class UDPClient:
    def __init__(self, client_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', client_port))
        self.rdt = None
        self.server_addr = (Config.SERVER_HOST, Config.SERVER_PORT)
        self.nome = None
    
    # ... (métodos existentes do cliente)
    
    def conectar(self):
        """Conecta ao servidor"""
        self.rdt = RDT(self.sock, self.server_addr)
    
    def enviar(self, mensagem):
        """Envia mensagem usando RDT"""
        if self.rdt:
            try:
                self.rdt.send(mensagem.encode())
                return True
            except Exception as e:
                print(f"❌ Erro ao enviar: {e}")
                return False
        return False
    
    def receber(self, timeout=None):
        """Recebe mensagem usando RDT"""
        if self.rdt:
            if timeout:
                # Configurar timeout no socket
                original_timeout = self.sock.gettimeout()
                self.sock.settimeout(timeout)
                try:
                    data = self.rdt.recv()
                    self.sock.settimeout(original_timeout)
                    if data:
                        return data.decode()
                    return None
                except socket.timeout:
                    self.sock.settimeout(original_timeout)
                    return None
                except Exception as e:
                    self.sock.settimeout(original_timeout)
                    print(f"❌ Erro ao receber: {e}")
                    return None
            else:
                try:
                    data = self.rdt.recv()
                    if data:
                        return data.decode()
                    return None
                except Exception as e:
                    print(f"❌ Erro ao receber: {e}")
                    return None
        return None
    
    def run(self):
        print("🎮 Cliente HuntCin UDP")
        print(f"📍 Porta local: {self.sock.getsockname()[1]}")
        
        # Conectar ao servidor
        self.conectar()
        
        # Login com múltiplas tentativas
        self.nome = input("Digite seu nome: ").strip()
        
        max_tentativas = 3
        tentativa = 0
        login_sucesso = False
        
        while tentativa < max_tentativas and not login_sucesso:
            tentativa += 1
            print(f"\nTentativa {tentativa} de {max_tentativas}...")
            
            try:
                # Enviar login usando RDT corretamente
                if not self.enviar(f"login {self.nome}"):
                    print("❌ Falha ao enviar login")
                    continue
                
                # Receber resposta com timeout
                resposta = self.receber(timeout=10)
                if resposta:
                    print(f"[Servidor]: {resposta}")
                    if "online" in resposta or "você está online" in resposta or "Login bem-sucedido" in resposta:
                        login_sucesso = True
                        print("✅ Login bem-sucedido!")
                        break
                    elif "não cadastrado" in resposta or "já está online" in resposta or "Porta incorreta" in resposta:
                        # Erro definitivo, não tentar novamente
                        print("❌ Erro no login, verifique seus dados.")
                        break
                    else:
                        print(f"⚠️ Resposta inesperada: {resposta}")
                else:
                    print(f"⏰ Timeout na tentativa {tentativa}")
                    
            except ConnectionResetError:
                print(f"❌ Conexão resetada pelo servidor na tentativa {tentativa}")
                # Recriar socket e RDT
                try:
                    local_port = self.sock.getsockname()[1]  # Obter a porta atual
                    self.sock.close()
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock.bind(('127.0.0.1', local_port))
                    self.conectar()
                except Exception as e:
                    print(f"❌ Não foi possível reconectar: {e}")
            except Exception as e:
                print(f"❌ Erro na tentativa {tentativa}: {e}")
                break
        
        if not login_sucesso:
            print("❌ Falha no login após múltiplas tentativas")
            return
        # ... resto do código ...
        
        # Aguardar início do jogo
        print("⏳ Aguardando início do jogo...")
        
        while True:
            mensagem = self.receber(timeout=30)
            
            if mensagem is None:
                print("⚠️ Nenhuma mensagem do servidor por 30 segundos")
                continuar = input("Deseja continuar aguardando? (s/n): ").strip().lower()
                if continuar != 's':
                    break
                continue
            
            print(f"\n[Servidor]: {mensagem}")
            
            # Verificar se é turno
            if "RODADA" in mensagem or "Digite seu comando:" in mensagem or "Você tem" in mensagem:
                print("⏰ Você tem 10 segundos para responder!")
                start = time.time()
                
                while time.time() - start < 10:
                    comando = input("> ").strip()
                    if comando:
                        if self.enviar(comando):
                            # Receber feedback
                            feedback = self.receber(timeout=5)
                            if feedback:
                                print(f"[Servidor]: {feedback}")
                                
                                # Verificar se encontrou tesouro
                                if "encontrou o tesouro" in feedback.lower():
                                    print("🎉 Parabéns! Você encontrou o tesouro!")
                                    return
                            else:
                                print("⚠️ Sem resposta do servidor")
                        break
                else:
                    print("⏰ Tempo esgotado!")
            
            # Verificar fim do jogo
            elif "FIM DO JOGO" in mensagem or "vencedor" in mensagem.lower():
                print("\n🎮 Jogo finalizado!")
                break
            
            elif "Estado atual" in mensagem or "Bem-vindo ao jogo" in mensagem:
                # Apenas mostrar estado
                continue
            
            elif "logout" in mensagem.lower() or "desconectado" in mensagem:
                print("❌ Você foi desconectado")
                break

if __name__ == "__main__":
    # Obter porta do usuário
    try:
        porta = int(input("Digite sua porta (ex: 5001, 5002, etc): "))
    except:
        print("❌ Porta inválida")
        exit(1)
    
    client = UDPClient(porta)
    client.run()