# server_udp.py
from network.connection_manager import ConnectionManager
from services.game_service import GameService
from utils.config import Config
from network.rdt import RDT
import socket

class UDPServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((Config.SERVER_HOST, Config.SERVER_PORT))
        self.sock.settimeout(1.0)
        
        self.connection_manager = ConnectionManager()
        self.game_service = GameService(self.connection_manager)
        
        print(f"🎮 Servidor HuntCin UDP iniciado em {Config.SERVER_HOST}:{Config.SERVER_PORT}")
    
    def run(self):
        """Loop principal do servidor"""
        self.connection_manager.carregar_contatos()
        
        while True:
            try:
                data, addr = self.sock.recvfrom(Config.BUFFER_SIZE)
                
                # Decidir se é login ou comando de jogo
                if self._is_jogador_conectado(addr):
                    self._processar_comando_jogo(data, addr)
                else:
                    self._processar_login(data, addr)
                    
            except socket.timeout:
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
        """Processa tentativa de login"""
        # Implementar lógica de login
        pass
    
    def _processar_comando_jogo(self, data, addr):
        """Processa comandos do jogo"""
        # Implementar lógica de comandos
        pass