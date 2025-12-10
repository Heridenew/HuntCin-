# services/game_services.py
import time
import os
from models.game import Game

class GameService:
    def __init__(self, connection_manager):
        self.game = None
        self.connection_manager = connection_manager
        self.jogo_iniciado = False
        self.rodada_atual = 0
        self.turno_timeout = 10
        self.deadline_turno = None
        self.comandos_rodada = set()
        self.pausa_pos_vitoria = False
    
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
        
        self.comandos_rodada = set()
        self.deadline_turno = time.time() + self.turno_timeout
        
        self._print_mapa_console()
        
        broadcast_inicio = (
            f"\n🔔 RODADA {self.rodada_atual + 1} iniciada! "
            f"Envie seu comando em até {self.turno_timeout}s."
        )
        self.enviar_para_todos(broadcast_inicio)

        for jogador in self.game.jogadores:
            def interno_para_humano(i, j):
                return (j + 1, 3 - i)
            x, y = interno_para_humano(*jogador.pos)
            
            msg = f"\n🔔 RODADA {self.rodada_atual + 1} iniciada!"
            msg += f"\n🎯 SUA VEZ!"
            msg += f"\n📍 Sua posição: ({x},{y})"
            msg += "\n🎮 Comandos: move up | move down | move left | move right | hint | suggest | logout"
            msg += f"\nHint: {'já usado' if jogador.hint_used else 'disponível (1 uso)'}"
            msg += f"\nSuggest: {'já usado' if jogador.suggest_used else 'disponível (1 uso)'}"
            msg += f"\n\n⏰ Você tem {self.turno_timeout} segundos!"
            msg += f"\n> Digite seu comando:"
            
            self.enviar_para_jogador(jogador.nome, msg)
            
            print(f"DEBUG: Turno enviado para {jogador.nome} pos=({x},{y})")
        
        print(f"Rodada {self.rodada_atual + 1}: comandos abertos para todos")
        time.sleep(0.5)  # Sincronização
    
    def processar_comando(self, jogador_nome, comando):
        """Processa comando do jogador (rodada simultânea)."""
        if not self.jogo_iniciado or not self.game:
            return False, "Jogo não iniciado", False
        if self.pausa_pos_vitoria:
            return False, "Partida encerrada. Aguardando reinício...", False
        
        jogador = next((p for p in self.game.jogadores if p.nome == jogador_nome), None)
        if not jogador:
            return False, "Jogador não encontrado", False
        
        # Verificar timeout antes de aceitar comando
        if self.deadline_turno and time.time() > self.deadline_turno:
            return False, "⏰ Tempo esgotado para este turno. Aguarde a próxima rodada.", False
        
        if jogador_nome in self.comandos_rodada:
            return False, "⚠️ Você já enviou comando nesta rodada.", False
        
        encontrou_tesouro, resposta = self.game.comando(jogador, comando)
        self.comandos_rodada.add(jogador_nome)

        if len(self.comandos_rodada) == len(self.game.jogadores):
            self.rodada_atual += 1
            self.enviar_estado_atual()
            self.iniciar_rodada()

        return encontrou_tesouro, resposta, True

    def tratar_timeout_turno(self):
        """Verifica deadline e fecha rodada simultânea se necessário."""
        if not self.jogo_iniciado or not self.game or not self.deadline_turno:
            return False
        
        agora = time.time()
        if agora <= self.deadline_turno and len(self.comandos_rodada) < len(self.game.jogadores):
            return False
        
        faltantes = [p.nome for p in self.game.jogadores if p.nome not in self.comandos_rodada]
        if faltantes:
            for nome in faltantes:
                self.enviar_para_jogador(nome, "\n⏰ Tempo esgotado! Você perdeu o turno.")
            self.enviar_para_todos(f"\n⏰ Jogadores sem ação: {', '.join(faltantes)}")
        
        self.rodada_atual += 1
        self.enviar_estado_atual()
        self.iniciar_rodada()
        return True

    def _print_mapa_console(self):
        """Imprime mapa atual no console do servidor."""
        if not self.game:
            return
        mapa = self.game.gerar_mapa()
        print("\n" + "="*20 + " MAPA ATUAL " + "="*20)
        for linha in mapa:
            print(" ".join(linha))
        print("="*50)

    def finalizar_vitoria(self, jogador_vencedor):
        """Incrementa placar e reinicia jogo com mesmo grupo."""
        self.pausa_pos_vitoria = True
        self.jogo_iniciado = False
        self.deadline_turno = None

        jogador_vencedor.score += 1
        ti, tj = self.game.tesouro
        x, y = (tj + 1, 3 - ti)
        mensagem_fim = (
            f"\nO jogador {jogador_vencedor.nome}:{jogador_vencedor.addr[1]} encontrou o tesouro na posição ({x},{y})!"
            f"\n🎉 {jogador_vencedor.nome.upper()} É O VENCEDOR!"
            f"\n⏳ Reiniciando em 30 segundos..."
        )
        self.enviar_para_todos(mensagem_fim)
        self.enviar_placar()
        
        time.sleep(30)

        if self.connection_manager.get_qtd_jogadores() >= 2:
            self.game = Game()
            for _, conn in self.connection_manager.connections.items():
                player = conn['player']
                self.game.add_player(player)
            self.rodada_atual = 0
            self.deadline_turno = None
            self.pausa_pos_vitoria = False
            self.enviar_para_todos("\n🔄 Novo tesouro sorteado! Reiniciando a partida.")
            self.enviar_estado_atual()
            self.iniciar_rodada()
        else:
            # Caso não haja jogadores suficientes, fica pausado
            self.game = None
            self.pausa_pos_vitoria = False

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
        if nome in self.comandos_rodada:
            self.comandos_rodada.discard(nome)
        if self.rodada_atual >= len(self.game.jogadores):
            self.rodada_atual = 0
        if len(self.game.jogadores) < 2:
            self.enviar_para_todos("\n⚠️ Jogadores insuficientes. Jogo pausado.")
            self.jogo_iniciado = False
            self.deadline_turno = None
            self.game = None