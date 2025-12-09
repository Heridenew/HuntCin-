# services/game_service.py
import time
from models.game import Game
from models.player import Player

class GameService:
    def __init__(self, connection_manager):
        self.game = None
        self.connection_manager = connection_manager
        self.jogo_iniciado = False
        self.rodada_atual = 0
        self.turno_timeout = 10
    
    def iniciar_jogo(self):
        """Inicia o jogo quando há jogadores suficientes"""
        if len(self.connection_manager.connections) >= 2 and not self.jogo_iniciado:
            self.game = Game()
            
            for nome, conn in self.connection_manager.connections.items():
                player = conn['player']
                self.game.add_player(player)
            
            self.jogo_iniciado = True
            self.rodada_atual = 0
            return True
        return False
    
    def processar_turno(self, jogador_nome, comando):
        """Processa o turno de um jogador"""
        # Lógica de processamento do turno
        pass
    
    def enviar_estado_para_todos(self):
        """Envia estado atual para todos os jogadores"""
        pass