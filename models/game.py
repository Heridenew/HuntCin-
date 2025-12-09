# models/game.py
import random

class Game:
    def __init__(self):
        self.jogadores = []
        self.mapa = [[0, 0, 0],
                     [0, 0, 0],
                     [0, 0, 0]]
        self.tesouro = self.spawn()
    
    def spawn(self):
        while True:
            x = random.randint(1,3)
            y = random.randint(1,3)
            if (x,y) != (1,1):
                return humano_para_interno(x,y)

    def add_player(self, player):
        player.pos = humano_para_interno(1,1)
        self.jogadores.append(player)

    def gerar_mapa(self):
        mapa = [["." for _ in range(3)] for __ in range(3)]

        # tesouro
        ti, tj = self.tesouro

        # jogadores
        for p in self.jogadores:
            i, j = p.pos
            if (i, j) == (ti, tj):
                mapa[i][j] = "T"
            else:
                mapa[i][j] = str(p.pid + 1)

        return mapa

    def comando(self, player, comando):
        i, j = player.pos
        
        # Converter "move up" para "up", etc
        comando_simples = comando
        if comando.lower().startswith("move "):
            comando_simples = comando[5:].lower().strip()

        # =====================
        #       MOVIMENTOS
        # =====================
        if comando_simples == "up":
            novo = (i - 1, j)
        elif comando_simples == "down":
            novo = (i + 1, j)
        elif comando_simples == "left":
            novo = (i, j - 1)
        elif comando_simples == "right":
            novo = (i, j + 1)

        # =====================
        #         HINT
        # =====================
        elif comando_simples == "hint":
            if player.hint_used:
                return False, "Você já usou sua dica."
            player.hint_used = True

            px, py = player.pos
            tx, ty = self.tesouro

            if px == tx and py == ty:
                return False, "Você está no tesouro!"

            # vertical tem prioridade
            if tx < px:
                return False, "Dica: o tesouro está acima."
            if tx > px:
                return False, "Dica: o tesouro está abaixo."

            # horizontal se estiver na mesma linha
            if ty > py:
                return False, "Dica: o tesouro está à direita."
            if ty < py:
                return False, "Dica: o tesouro está à esquerda."

        # =====================
        #       SUGGEST
        # =====================
        elif comando_simples == "suggest":
            if player.suggest_used:
                return False, "Você já usou sua sugestão."
            player.suggest_used = True

            px, py = player.pos
            tx, ty = self.tesouro

            if px == tx and py == ty:
                return False, "Você está no tesouro!"

            if tx < px:
                return False, "Sugestão: move up"
            if tx > px:
                return False, "Sugestão: move down"
            if ty > py:
                return False, "Sugestão: move right"
            if ty < py:
                return False, "Sugestão: move left"

        else:
            return False, "Comando inválido."

        # =====================
        #   PROCESSAR MOVIMENTO
        # =====================
        if comando_simples in ["up", "down", "left", "right"]:
            ni, nj = novo

            if 0 <= ni < 3 and 0 <= nj < 3:
                player.pos = (ni, nj)
            else:
                return False, "Movimento inválido."

            if player.pos == self.tesouro:
                return True, "Você encontrou o tesouro!"

            return False, "Movimento realizado."