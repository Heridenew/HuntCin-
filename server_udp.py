# server_udp.py
from network.connection_manager import ConnectionManager
from services.game_services import GameService  # Importação DIRETA
from network.rdt import RDT
from models.player import Player
import socket
import time
from utils.config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE  # Importar VARIÁVEIS, não classe

class UDPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((SERVER_HOST, SERVER_PORT))  # Usar VARIÁVEIS
        self.sock.settimeout(1.0)
        
        self.connection_manager = ConnectionManager()
        self.game_service = GameService(self.connection_manager)
        self.rdt_instances = {}
        
        print(f"🎮 Servidor HuntCin UDP iniciado em {SERVER_HOST}:{SERVER_PORT}")
    
    def run(self):
        """Loop principal do servidor"""
        self.connection_manager.carregar_contatos()
        
        print("\n🎮 Servidor HuntCin UDP - PRONTO")
        print(f"Aguardando jogadores (mínimo: 2)...")
        print("=" * 50)
        
        while True:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)  # Usar VARIÁVEL
                
                # Decidir se é login ou comando de jogo
                if self._is_jogador_conectado(addr):
                    self._processar_comando_jogo(data, addr)
                else:
                    self._processar_login(data, addr)
                    
            except socket.timeout:
                # oportunidade para tratar timeouts de turno
                self.game_service.tratar_timeout_turno()
                continue
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                continue
    
    def _is_jogador_conectado(self, addr):
        """Verifica se endereço pertence a jogador conectado"""
        for conn in self.connection_manager.get_all_connections():
            if conn['addr'] == addr:
                return True
        return False
    
    def _processar_login(self, data, addr):
        if addr not in self.rdt_instances:
            self.rdt_instances[addr] = RDT(self.sock, addr)   
        try:
            # Reutilizar instância RDT por cliente
            rdt = self.rdt_instances[addr]
            
            # Processar o pacote recebido
            seq, mensagem_bytes, checksum_ok = rdt.parse_packet(data)
            
            if seq is None or not checksum_ok:
                print(f"   ❌ Pacote RDT inválido de {addr}")
                # Enviar ACK
                ack = b'\x00' if seq is None else bytes([seq])
                self.sock.sendto(ack, addr)
                return
            
            # Enviar ACK para o pacote recebido
            ack_packet = seq.to_bytes(1, 'big')
            self.sock.sendto(ack_packet, addr)
            
            # Decodificar mensagem
            mensagem = mensagem_bytes.decode('utf-8', errors='ignore').strip()
            print(f"   📩 Login recebido de {addr}: {mensagem}")
            
            if not mensagem.lower().startswith("login "):
                erro_msg = "Comando inválido. Use: login <nome>"
                self.sock.sendto(erro_msg.encode(), addr)
                return
            
            partes = mensagem.split()
            if len(partes) != 2:
                erro_msg = "Formato inválido. Use: login <nome>"
                self.sock.sendto(erro_msg.encode(), addr)
                return
            
            nome = partes[1]
            
            # Validar login
            sucesso, resposta = self.connection_manager.validar_login(nome, addr)
            
            # server_udp.py - Linhas 105-110 - VERSÃO CORRIGIDA
            if sucesso:
                # Criar jogador
                pid = self.connection_manager.get_qtd_jogadores()
                player = Player(pid, addr, nome=nome)
                
                # Adicionar conexão
                self.connection_manager.adicionar_conexao(nome, addr, rdt, player)
                
                # Enviar resposta EXATA conforme requisito
                resposta_final = "você está online!"
                rdt.send(resposta_final.encode())
                
                print(f"✅ {nome} conectado de {addr} (PID: {pid})")  # APENAS PRINT, NÃO ENVIAR
                
                # Verificar se podemos iniciar o jogo
                if self.game_service.iniciar_jogo():
                    print("🎮 JOGO INICIADO!")
            else:
                # Enviar erro
                try:
                    rdt.send(resposta.encode())
                except:
                    self.sock.sendto(resposta.encode(), addr)
                    
        except Exception as e:
            print(f"❌ Erro processando login: {e}")
    
    def _processar_comando_jogo(self, data, addr):
        """Processa comandos do jogo"""
        try:
            # Encontrar jogador pelo endereço
            jogador_nome, conn = self.connection_manager.get_jogador_por_addr(addr)
            
            if not jogador_nome or not conn:
                return
            
            # Processar como pacote RDT
            rdt = conn['rdt']
            seq, mensagem_bytes, checksum_ok = rdt.parse_packet(data)
            
            if not checksum_ok or seq is None:
                print(f"   ❌ Pacote RDT inválido de {jogador_nome}")
                return
            
            comando = mensagem_bytes.decode('utf-8', errors='ignore').strip()
            print(f"   📥 Comando de {jogador_nome}: {comando}")

            # Logout
            if comando.lower() == "logout":
                rdt.send("Logout realizado. Até mais!".encode())
                self.game_service.remover_jogador(jogador_nome)
                self.connection_manager.remover_conexao(jogador_nome)
                if addr in self.rdt_instances:
                    del self.rdt_instances[addr]
                return
            
            # Processar comando
            encontrou_tesouro, resposta, consumiu_turno = self.game_service.processar_comando(jogador_nome, comando)
            
            # Enviar resposta ao jogador
            rdt.send(resposta.encode())
            
            if encontrou_tesouro:
                # FIM DO JOGO e reinício com mesmo grupo
                self.game_service.finalizar_vitoria(conn['player'])
            elif consumiu_turno:
                # Enviar estado atual para todos
                self.game_service.enviar_estado_atual()
                
                # Próxima rodada
                self.game_service.rodada_atual += 1
                time.sleep(1)
                self.game_service.iniciar_rodada()
                
        except Exception as e:
            print(f"❌ Erro processando comando: {e}")

if __name__ == "__main__":
    server = UDPServer()
    server.run()