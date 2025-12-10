# client_udp.py - VERSÃO CORRIGIDA COM THREADING
import socket
import time
import threading
import queue
import sys
import re
from network import RDT
from utils.config import SERVER_HOST, SERVER_PORT  # Importar variáveis

# Silenciar logs de debug/info do RDT no cliente para não poluir o prompt
import logging
logging.getLogger().setLevel(logging.WARNING)

# Evitar falhas de encoding em terminais Windows (cp1252)
try:
    import sys
    sys.stdout.reconfigure(errors="ignore")
    sys.stderr.reconfigure(errors="ignore")
except Exception:
    pass

class UDPClient:
    def __init__(self, client_port, nome=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', client_port))
        self.rdt = None
        self.server_addr = (SERVER_HOST, SERVER_PORT)  # Usar variáveis
        self.nome = nome
        # Lock para sincronizar envio/recepção RDT e evitar perda de ACKs
        self.rdt_lock = threading.Lock()
        # Controle de rodada já exibida para evitar duplicidade de prompt
        self.last_round_shown = None
        
        # Threading para recepção não-bloqueante
        self.message_queue = queue.Queue()
        self.receiving_thread = None
        self.receiving_active = False
    
    def conectar(self):
        """Conecta ao servidor"""
        self.rdt = RDT(self.sock, self.server_addr)
    
    def enviar(self, mensagem):
        """Envia mensagem usando RDT"""
        if self.rdt:
            try:
                # Serializar acesso ao RDT para não colidir com recv()
                with self.rdt_lock:
                    self.rdt.send(mensagem.encode())
                return True
            except Exception as e:
                print(f"❌ Erro ao enviar: {e}")
                return False
        return False
    
    def _receiver_thread(self):
        """Thread que recebe mensagens continuamente do servidor"""
        while self.receiving_active:
            try:
                if self.rdt:
                    # Usar timeout curto para permitir verificação periódica do flag
                    with self.rdt_lock:
                        data = self.rdt.recv(timeout=0.3)
                    if data:
                        # Ignorar pacotes de 1 byte (ACK) que podem chegar aqui
                        if len(data) == 1:
                            continue
                        mensagem = data.decode()
                        # Guardar na fila para o loop principal
                        # Evitar enfileirar mensagens de rodada duplicadas
                        msg_lower = mensagem.lower()
                        round_match = re.search(r'rodada\s+(\d+)', msg_lower)
                        if round_match:
                            round_num = int(round_match.group(1))
                            if round_num == self.last_round_shown:
                                # Já mostramos esta rodada; não enfileirar de novo
                                continue
                            self.last_round_shown = round_num
                        self.message_queue.put(mensagem)

                        # Exibir imediatamente somente mensagens de broadcast
                        # (rodada, tempo esgotado, estado, vencedor/tesouro).
                        # Respostas individuais ficam só na fila para evitar duplicidade.
                        try:
                            is_broadcast = (
                                ("rodada" in msg_lower and "iniciada" in msg_lower) or
                                ("tempo esgotado" in msg_lower) or
                                ("estado atual" in msg_lower) or
                                ("jogadores sem ação" in msg_lower) or
                                ("vencedor" in msg_lower) or
                                ("encontrou o tesouro" in msg_lower)
                            )
                            if is_broadcast:
                                sep = "\n" + "="*60
                                if "rodada" in msg_lower and "iniciada" in msg_lower:
                                    print(f"{sep}\n{mensagem}\nComandos: move up | move down | move left | move right | hint | suggest | logout\n" + "="*60)
                                elif ("vencedor" in msg_lower) or ("encontrou o tesouro" in msg_lower):
                                    print(f"{sep}\n🏆 {mensagem}\n" + "="*60)
                                else:
                                    print(f"{sep}\n{mensagem}\n" + "="*60)
                                sys.stdout.flush()
                        except Exception:
                            pass
            except socket.timeout:
                # Timeout é esperado, continuar
                continue
            except Exception as e:
                if self.receiving_active:
                    # Apenas logar se ainda estiver ativo
                    logging.debug(f"Erro na thread de recepção: {e}")
                break
    
    def receber(self, timeout=None):
        """Recebe mensagem usando RDT (método legado para compatibilidade)"""
        if self.rdt:
            try:
                data = self.rdt.recv(timeout=timeout)
                if data:
                    return data.decode()
                return None
            except socket.timeout:
                return None
            except Exception as e:
                print(f"❌ Erro ao receber: {e}")
                return None
        return None
    
    def receber_mensagem(self, timeout=None):
        """Recebe mensagem da queue (não bloqueia recepção)"""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def run(self):
        print("🎮 Cliente HuntCin UDP")
        print(f"📍 Porta local: {self.sock.getsockname()[1]}")
        
        # Conectar ao servidor
        self.conectar()
        
        # Login com múltiplas tentativas
        if not self.nome:
            self.nome = input("Digite seu nome: ").strip()
        
        max_tentativas = 3
        tentativa = 0
        login_sucesso = False
        
        while tentativa < max_tentativas and not login_sucesso:
            tentativa += 1
            print(f"\nTentativa {tentativa} de {max_tentativas}...")
            
            try:
                # Enviar login usando RDT
                if not self.enviar(f"login {self.nome}"):
                    print("❌ Falha ao enviar login")
                    continue
    
                # Receber resposta com timeout
                resposta = self.receber(timeout=10)
                if resposta:
                    print(f"[Servidor]: {resposta}")
                    if ("você está online!" in resposta.lower() or
                        "bem-vindo" in resposta.lower() or
                        "estado atual" in resposta.lower()):
                        login_sucesso = True
                        print("✅ Login bem-sucedido!")
                        
                        # AGUARDAR MAIS JOGADORES
                        print("👥 Aguardando mais jogadores para iniciar o jogo...")
                        
                        while True:
                            status = self.receber(timeout=30)
                            if status and ("JOGO INICIADO" in status or "BEM-VINDO" in status):
                                print(f"[Servidor]: {status}")
                                break
                            elif status:
                                print(f"[Servidor]: {status}")
                        
                        break  # Sair do loop de tentativas
                    
            except ConnectionResetError:
                print(f"❌ Conexão resetada pelo servidor na tentativa {tentativa}")
                # Recriar socket e RDT
                try:
                    local_port = self.sock.getsockname()[1]
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
        
        # Aguardar início do jogo
        print("⏳ Aguardando início do jogo...")
        
        # Iniciar thread de recepção
        self.receiving_active = True
        self.receiving_thread = threading.Thread(target=self._receiver_thread, daemon=True)
        self.receiving_thread.start()
        
        # Contador para timeout de espera
        ultima_mensagem_time = time.time()
        timeout_espera = 30
        
        while True:
            # Tentar receber mensagem da queue (não bloqueia)
            mensagem = self.receber_mensagem(timeout=0.1)
            
            if mensagem:
                ultima_mensagem_time = time.time()  # Resetar contador
                
                # Verificar se é turno
                if "RODADA" in mensagem or "Digite seu comando:" in mensagem or "Sua posição:" in mensagem:
                    # Mensagens de rodada já foram exibidas pela thread de recepção (evita duplicidade)
                    
                    # AGORA input() não bloqueia a recepção porque está em thread separada!
                    try:
                        comando = " ".join(input("> ").strip().lower().split())
                    except (EOFError, KeyboardInterrupt):
                        comando = "logout"
                    
                    if comando:
                        if comando.lower() == "logout":
                            self.enviar("logout")
                            print("Saindo do jogo...")
                            break
                        
                        if self.enviar(comando):
                            # Aguardar feedback (com timeout)
                            feedback = self.receber_mensagem(timeout=5)
                            if feedback:
                                print(f"[Servidor]: {feedback}")
                                if "encontrou o tesouro" in feedback.lower():
                                    print("🎉 Parabéns! Tesouro encontrado! Aguardando reinício...")
                                    # Não sair: aguardar a pausa/reinício do servidor
                                    continue
                            else:
                                print("⚠️ Sem resposta do servidor")
                    else:
                        print("⏰ Sem comando enviado.")
                
                # Verificar fim do jogo
                elif "FIM DO JOGO" in mensagem or "vencedor" in mensagem.lower():
                    print("\n🎮 Jogo finalizado!")
                    break
                
                elif "Estado atual" in mensagem or "Bem-vindo ao jogo" in mensagem:
                    # Apenas mostrar estado
                    print(mensagem)
                    continue
                
                elif "logout" in mensagem.lower() or "desconectado" in mensagem:
                    print("❌ Você foi desconectado")
                    break
                else:
                    # Outras mensagens - apenas mostrar
                    print(mensagem)
            
            # Verificar timeout de espera
            elif time.time() - ultima_mensagem_time > timeout_espera:
                print("⚠️ Nenhuma mensagem do servidor por 30 segundos")
                try:
                    continuar = input("Deseja continuar aguardando? (s/n): ").strip().lower()
                    if continuar != 's':
                        self.enviar("logout")
                        break
                    ultima_mensagem_time = time.time()  # Resetar contador
                except (EOFError, KeyboardInterrupt):
                    self.enviar("logout")
                    break
            
            # Verificar se thread de recepção ainda está ativa
            if not self.receiving_thread.is_alive() and self.receiving_active:
                print("❌ Thread de recepção parou inesperadamente")
                break
        
        # Limpar recursos
        self.receiving_active = False
        if self.receiving_thread and self.receiving_thread.is_alive():
            self.receiving_thread.join(timeout=1)

if __name__ == "__main__":
    import sys as _sys
    args = _sys.argv[1:]
    porta = None
    nome_cli = None
    if args:
        # Aceita: python client_udp.py --port 5000 --name teste1
        if "--port" in args:
            try:
                porta = int(args[args.index("--port") + 1])
            except Exception:
                porta = None
        if "--name" in args:
            try:
                nome_cli = args[args.index("--name") + 1]
            except Exception:
                nome_cli = None
    if porta is None:
        try:
            porta = int(input("Digite sua porta (ex: 5001, 5002, etc): "))
        except:
            print("❌ Porta inválida")
            exit(1)
    
    client = UDPClient(porta, nome=nome_cli)
    client.run()