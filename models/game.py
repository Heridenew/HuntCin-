# models/game.py
import random

def humano_para_interno(x, y):
    """Converte coordenadas humanas (x,y) para internas (i,j)"""
    # (1,1) → (2,0)
    # (1,2) → (1,0)
    # (1,3) → (0,0)
    # (3,3) → (0,2)
    return (3 - y, x - 1)

def interno_para_humano(i, j):
    """Converte coordenadas internas (i,j) para humanas (x,y)"""
    # (0,0) → (1,3)
    # (2,0) → (1,1)
    # (0,2) → (3,3)
    return (j + 1, 3 - i)

class Game:
    def __init__(self):
        self.jogadores = []
        self.mapa = [[0,0,0],
                     [0,0,0],
                     [0,0,0]]
        self.tesouro = self.spawn()

    def spawn(self):
        """Sorteia tesouro em qualquer posição exceto (1,1)"""
        while True:
            x = random.randint(1,3)
            y = random.randint(1,3)
            if (x,y) != (1,1):  # Não pode ser na posição inicial
                return humano_para_interno(x, y)

    def add_player(self, player):
        """Adiciona jogador na posição inicial (1,1)"""
        player.reset_for_new_game()
        player.pos = humano_para_interno(1, 1)  # (1,1) em coordenadas humanas
        self.jogadores.append(player)

    def gerar_mapa(self):
        """Gera representação do mapa"""
        mapa = [["." for _ in range(3)] for __ in range(3)]

        # Marcar tesouro
        ti, tj = self.tesouro

        # Marcar jogadores
        for p in self.jogadores:
            i, j = p.pos
            if (i, j) == (ti, tj):
                pass
            else:
                mapa[i][j] = str(p.pid + 1)

        return mapa

    def comando(self, player, comando):
        """Processa comando do jogador"""
        i, j = player.pos
        
        # =====================
        #       MOVIMENTOS
        # =====================
        if comando == "move up":
            novo = (i - 1, j)
        elif comando == "move down":
            novo = (i + 1, j)
        elif comando == "move left":
            novo = (i, j - 1)
        elif comando == "move right":
            novo = (i, j + 1)

        # =====================
        #         HINT
        # =====================
        elif comando == "hint":
            if player.hint_used:
                return False, "Você já usou sua dica."
            player.hint_used = True

            px, py = player.pos
            tx, ty = self.tesouro

            if px == tx and py == ty:
                return False, "Você está no tesouro!"

            # Dica de direção
            if tx < px:
                return False, "O tesouro está mais acima."
            elif tx > px:
                return False, "O tesouro está mais abaixo."
            elif ty > py:
                return False, "O tesouro está mais à direita."
            else:
                return False, "O tesouro está mais à esquerda."

        # =====================
        #       SUGGEST
        # =====================
        elif comando == "suggest":
            if player.suggest_used:
                return False, "Você já usou sua sugestão."
            player.suggest_used = True

            px, py = player.pos
            tx, ty = self.tesouro

            if px == tx and py == ty:
                return False, "Você está no tesouro!"

            # Calcula direção principal
            if tx < px:  # Tesouro está acima
                casas = px - tx
                return False, f"Sugestão: move up {casas} casa{'s' if casas > 1 else ''}."
            elif tx > px:  # Tesouro está abaixo
                casas = tx - px
                return False, f"Sugestão: move down {casas} casa{'s' if casas > 1 else ''}."
            elif ty > py:  # Tesouro está à direita
                casas = ty - py
                return False, f"Sugestão: move right {casas} casa{'s' if casas > 1 else ''}."
            else:  # Tesouro está à esquerda
                casas = py - ty
                return False, f"Sugestão: move left {casas} casa{'s' if casas > 1 else ''}."

        # =====================
        #   PROCESSAR MOVIMENTO
        # =====================
        if comando.startswith("move "):
            ni, nj = novo

            # Verificar limites do grid
            if 0 <= ni < 3 and 0 <= nj < 3:
                player.pos = (ni, nj)
                # Converter para coordenadas humanas para mensagem
                x, y = interno_para_humano(ni, nj)
                
                if player.pos == self.tesouro:
                    tx, ty = interno_para_humano(*self.tesouro)
                    return True, f"O jogador {player.nome} encontrou o tesouro na posição ({tx},{ty})!"
                
                return False, f"Movimento realizado. Nova posição: ({x},{y})"
            else:
                return False, "Movimento inválido. Fora do grid."