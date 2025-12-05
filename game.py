import random
import os

def humano_para_interno(x, y):
    return (3 - y, x - 1)

def interno_para_humano(i, j):
    return (j + 1, 3 - i)

class Game:
    def __init__(self):
        self.jogadores = []
        self.mapa = [[0,0,0],
                     [0,0,0],
                     [0,0,0]]
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

        for p in self.jogadores:
            i, j = p.pos
            mapa[i][j] = str(p.pid + 1)

        return mapa

    def comando(self, player, comando):
        i, j = player.pos

        if comando == "up":
            novo = (i - 1, j)
        elif comando == "down":
            novo = (i + 1, j)
        elif comando == "left":
            novo = (i, j - 1)
        elif comando == "right":
            novo = (i, j + 1)
        elif comando == "hint":
            if player.hint_usado:
                return False, "Você já usou sua dica."
            player.hint_usado = True

            tx, ty = self.tesouro
            px, py = player.pos

            if tx < px:
                return False, "Dica: o tesouro está acima."
            elif tx > px:
                return False, "Dica: o tesouro está abaixo."
            elif ty > py:
                return False, "Dica: o tesouro está à direita."
            elif ty < py:
                return False, "Dica: o tesouro está à esquerda."
            else:
                return False, "Você está no tesouro!"
        elif comando == "suggest":
            if player.suggest_usado:
                return False, "Você já usou sua sugestão."

            player.suggest_usado = True

            tx, ty = self.tesouro
            px, py = player.pos

            if tx < px:
                return False, "Sugestão: up"
            elif tx > px:
                return False, "Sugestão: down"
            elif ty > py:
                return False, "Sugestão: right"
            elif ty < py:
                return False, "Sugestão: left"
            else:
                return False, "Você está no tesouro!"
        else:
            return False, "Comando inválido."

        # movimento
        ni, nj = novo
        if 0 <= ni < 3 and 0 <= nj < 3:
            player.pos = (ni, nj)
        else:
            return False, "Movimento inválido."

        if player.pos == self.tesouro:
            return True, "Você encontrou o tesouro!"

        return False, "Movimento realizado."
