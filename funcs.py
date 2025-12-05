# funcs.py
import random

def spawn():
    pos = (random.randint(0, 2), random.randint(0, 2))
    while pos == (0,0):
        pos = (random.randint(0, 2), random.randint(0, 2))
    return pos

def checarsepode(delta, atual):
    x, y = atual
    px = x + delta[0]
    py = y + delta[1]
    return 0 <= px <= 2 and 0 <= py <= 2

def mover(choose, atual):
    direcoes = {
        "up":    (-1, 0),
        "down":  (1, 0),
        "left":  (0, -1),
        "right": (0, 1)
    }

    if choose not in direcoes:
        return atual, "Movimento inválido!"

    delta = direcoes[choose]

    if checarsepode(delta, atual):
        return (atual[0] + delta[0], atual[1] + delta[1]), ""
    else:
        return atual, "Movimentação não permitida!"

def hint(player, tesouro):
    if player.hint_used:
        return "Você já usou sua dica."

    player.hint_used = True
    ax, ay = player.pos
    tx, ty = tesouro

    if tx < ax:
        return "Dica: o tesouro está acima de você."
    if tx > ax:
        return "Dica: o tesouro está abaixo de você."
    if ty > ay:
        return "Dica: o tesouro está à direita de você."
    if ty < ay:
        return "Dica: o tesouro está à esquerda de você."
    return "Você já está no tesouro!"

def suggest(player, tesouro):
    if player.suggest_used:
        return "Você já usou sua sugestão."

    player.suggest_used = True
    ax, ay = player.pos
    tx, ty = tesouro

    if tx < ax:
        return "Sugestão: mova up."
    if tx > ax:
        return "Sugestão: mova down."
    if ty > ay:
        return "Sugestão: mova right."
    if ty < ay:
        return "Sugestão: mova left."
    return "Você já está no tesouro!"
