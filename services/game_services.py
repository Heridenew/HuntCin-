# services/game_services.py
import time
from models.game import Game  # Importar no topo

class GameService:
    def __init__(self, connection_manager):
        self.game = None  # Instância será criada depois
        self.connection_manager = connection_manager
        self.jogo_iniciado = False
        self.rodada_atual = 0
        self.turno_timeout = 10
        self.deadline_turno = None
    
    def iniciar_jogo(self):
        """Inicia o jogo quando há jogadores suficientes"""
        if self.connection_manager.get_qtd_jogadores() >= 2 and not self.jogo_iniciado:
            print(f"\n🎮 INICIANDO JOGO com {self.connection_manager.get_qtd_jogadores()} jogadores!")
            
            self.game = Game()
            
            for nome, conn in self.connection_manager.connections.items():
                player = conn['player']
                self.game.add_player(player)
                print(f"   ➤ {nome} na posição inicial (1,1)")
            
            self.jogo_iniciado = True
            self.rodada_atual = 0
            self.deadline_turno = None
            
            self.enviar_para_todos("\n🎮 BEM-VINDO AO HUNTCIN! 🎮")
            self.enviar_estado_atual()
            
            self.iniciar_rodada()
            return True
        return False
    
    def enviar_para_todos(self, mensagem):
        """Envia mensagem para todos os jogadores"""
        self.connection_manager.broadcast(mensagem)
    
    def enviar_para_jogador(self, nome, mensagem):
        """Envia mensagem para um jogador específico"""
        conn = self.connection_manager.get_conexao(nome)
        if conn:
            try:
                conn['rdt'].send(mensagem.encode())
                return True
            except:
                pass
        return False
    
    def enviar_estado_atual(self):
        """Envia estado atual do grid para todos"""
        if not self.game or not self.game.jogadores:
            return
        
        # Função de conversão local
        def interno_para_humano(i, j):
            return (j + 1, 3 - i)
        
        estado = "[Servidor] Estado atual: "
        jogadores_info = []
        
        for p in self.game.jogadores:
            x, y = interno_para_humano(*p.pos)
            jogadores_info.append(f"{p.nome}({x},{y})")
        
        estado += ", ".join(jogadores_info)
        self.enviar_para_todos(estado)
    
    def iniciar_rodada(self):
        """Inicia uma nova rodada do jogo"""
        if not self.game or not self.game.jogadores:
            return
        
        # Determinar jogador da vez
        jogador_idx = self.rodada_atual % len(self.game.jogadores)
        jogador = self.game.jogadores[jogador_idx]
        nome_jogador = jogador.nome
        
        # Converter posição
        def interno_para_humano(i, j):
            return (j + 1, 3 - i)
        
        x, y = interno_para_humano(*jogador.pos)
        
        # Mensagens
        broadcast_inicio = (
            f"\n🔔 RODADA {self.rodada_atual + 1} iniciada! "
            f"Jogador da vez: {nome_jogador}"
        )
        self.enviar_para_todos(broadcast_inicio)
        
        mensagem_turno = f"\n🎯 RODADA {self.rodada_atual + 1} - SUA VEZ!"
        mensagem_turno += f"\n📍 Sua posição: ({x},{y})"
        mensagem_turno += f"\n🎮 Comandos: move up/down/left/right"
        if not jogador.hint_used:
            mensagem_turno += f"\n           hint (1 uso)"
        if not jogador.suggest_used:
            mensagem_turno += f"\n           suggest (1 uso)"
        mensagem_turno += f"\n\n⏰ Você tem {self.turno_timeout} segundos!"
        mensagem_turno += f"\n> Digite seu comando:"
        
        self.enviar_para_jogador(nome_jogador, mensagem_turno)
        
        # Aviso para outros
        for outro in self.game.jogadores:
            if outro.nome != nome_jogador:
                mensagem_espera = f"\n⏳ Aguarde... É a vez de {nome_jogador}"
                self.enviar_para_jogador(outro.nome, mensagem_espera)
        
        self.deadline_turno = time.time() + self.turno_timeout
        print(f"🎮 Rodada {self.rodada_atual + 1}: Vez de {nome_jogador}")
    
    def processar_comando(self, jogador_nome, comando):
        """Processa comando do jogador"""
        if not self.jogo_iniciado or not self.game:
            return False, "Jogo não iniciado", False
        
        # Verificar se é a vez deste jogador
        if self.rodada_atual >= len(self.game.jogadores):
            self.rodada_atual = 0
        
        jogador_idx = self.rodada_atual % len(self.game.jogadores)
        jogador_da_vez = self.game.jogadores[jogador_idx]
        
        if jogador_da_vez.nome != jogador_nome:
            return False, "⚠️ Não é sua vez! Aguarde seu turno.", False
        
        # Verificar timeout antes de aceitar comando
        if self.deadline_turno and time.time() > self.deadline_turno:
            return False, "⏰ Tempo esgotado para este turno. Aguarde a próxima rodada.", False
        
        # Processar comando
        encontrou_tesouro, resposta = self.game.comando(jogador_da_vez, comando)
        return encontrou_tesouro, resposta, True

    def tratar_timeout_turno(self):
        """Verifica deadline e pula turno se necessário."""
        if not self.jogo_iniciado or not self.game or not self.deadline_turno:
            return False
        
        if time.time() <= self.deadline_turno:
            return False
        
        # Tempo esgotado
        jogador_idx = self.rodada_atual % len(self.game.jogadores)
        jogador = self.game.jogadores[jogador_idx]
        msg_jogador = "\n⏰ Tempo esgotado! Você perdeu o turno."
        self.enviar_para_jogador(jogador.nome, msg_jogador)
        self.enviar_para_todos(f"\n⏰ {jogador.nome} perdeu o turno por tempo.")
        
        # Avançar rodada
        self.rodada_atual += 1
        self.enviar_estado_atual()
        self.iniciar_rodada()
        return True

    def finalizar_vitoria(self, jogador_vencedor):
        """Incrementa placar e reinicia jogo com mesmo grupo."""
        jogador_vencedor.score += 1
        ti, tj = self.game.tesouro
        x, y = (tj + 1, 3 - ti)
        mensagem_fim = (
            f"\nO jogador {jogador_vencedor.nome}:{jogador_vencedor.addr[1]} encontrou o tesouro na posição ({x},{y})!"
            f"\n🎉 {jogador_vencedor.nome.upper()} É O VENCEDOR!"
        )
        self.enviar_para_todos(mensagem_fim)
        self.enviar_placar()
        
        # Reiniciar mantendo jogadores conectados
        self.game = Game()
        for _, conn in self.connection_manager.connections.items():
            player = conn['player']
            self.game.add_player(player)
        self.rodada_atual = 0
        self.deadline_turno = None
        self.enviar_para_todos("\n🔄 Novo tesouro sorteado! Reiniciando a partida.")
        self.enviar_estado_atual()
        self.iniciar_rodada()

    def enviar_placar(self):
        """Envia placar atual para todos."""
        if not self.game:
            return
        placar = "🏆 Placar: " + ", ".join([f"{p.nome}={p.score}" for p in self.game.jogadores])
        self.enviar_para_todos(placar)

    def remover_jogador(self, nome):
        """Remove jogador do game e ajusta rodada."""
        if not self.game:
            return
        self.game.jogadores = [p for p in self.game.jogadores if p.nome != nome]
        # Ajustar rodada para evitar índice fora
        if self.rodada_atual >= len(self.game.jogadores):
            self.rodada_atual = 0
        # Se ficar menos de 2, encerrar jogo
        if len(self.game.jogadores) < 2:
            self.enviar_para_todos("\n⚠️ Jogadores insuficientes. Jogo pausado.")
            self.jogo_iniciado = False
            self.deadline_turno = None
            self.game = None