import os
import random

def checarsepode(delta, atual):
    # delta é uma tupla, tipo (1,0)
    prox_x = atual[0] + delta[0]
    prox_y = atual[1] + delta[1]

    # limites do tabuleiro 3x3
    if prox_x > 2 or prox_x < 0 or prox_y > 2 or prox_y < 0:
        return False

    return True


def movimentacao(choose, atual):
    direcoes = {
        "up":    (-1, 0),
        "down":  (1, 0),
        "left":  (0, -1),
        "right": (0, 1)
    }

    if choose not in direcoes:
        print("Movimento inválido!")
        return atual

    delta = direcoes[choose]

    if checarsepode(delta, atual):
        return (atual[0] + delta[0], atual[1] + delta[1])
    else:
        return atual


def markmap(atual, mapa):
    # zera o mapa inteiro e marca apenas a posição atual com 1
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            mapa[i][j] = 0
    mapa[atual[0]][atual[1]] = 1
    return mapa

def spawn():
    x = random.randint(1, 3)
    y = random.randint(1, 3)

    # converter (x,y) => índices Python
    matriz_x = 3 - y       # inverte o eixo vertical
    matriz_y = x - 1

    # evitar spawn na posição inicial (2,0)
    while (matriz_x, matriz_y) == (2,0):
        x = random.randint(1, 3)
        y = random.randint(1, 3)
        matriz_x = 3 - y
        matriz_y = x - 1

    return (matriz_x, matriz_y)


def hint(hint_usado, tesouro, atual):
    if hint_usado:
        return hint_usado, "Você já usou sua dica."

    hint_usado = True

    if tesouro[0] < atual[0]:
        return hint_usado, "Dica: o tesouro está mais acima."
    elif tesouro[0] > atual[0]:
        return hint_usado, "Dica: o tesouro está mais abaixo."
    elif tesouro[1] > atual[1]:
        return hint_usado, "Dica: o tesouro está mais à direita."
    elif tesouro[1] < atual[1]:
        return hint_usado, "Dica: o tesouro está mais à esquerda."
    else:
        return hint_usado, "Você já está na posição do tesouro!"

            
def suggest(suggest_usado, tesouro, atual):
    if suggest_usado:
        return suggest_usado, "Você já usou sua sugestão."

    suggest_usado = True

    if tesouro[0] < atual[0]:
        return suggest_usado, "Sugestão: move up."
    elif tesouro[0] > atual[0]:
        return suggest_usado, "Sugestão: move down."
    elif tesouro[1] > atual[1]:
        return suggest_usado, "Sugestão: move right."
    elif tesouro[1] < atual[1]:
        return suggest_usado, "Sugestão: move left."
    else:
        return suggest_usado, "Você já está na posição do tesouro!"


def game():
    mapa = [
        [0,0,0],
        [0,0,0],
        [0,0,0]
    ]

    tesouro = spawn()
    print("Você começará na posição (0,0).")
    atual = (2,0)
    markmap(atual, mapa)

    mensagem = ""
    hint_usado = False
    suggest_usado = False

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')

        for linha in mapa:
            print(linha)

        # converte para o sistema humano
        x_h = atual[1] + 1
        y_h = 3 - atual[0]

        print(f"Sua posição atual é ({x_h},{y_h})")

        if atual == tesouro:
            print("Parabéns, você achou o tesouro e ganhou o jogo!!!")
            break

        if mensagem:
            print(mensagem)

        mov = input("Movimento (up, down, left, right, hint, suggest ou quit): ").strip().lower()

        if mov == "quit":
            print("Encerrando o jogo.")
            break

        if mov == "hint":
            hint_usado, mensagem = hint(hint_usado, tesouro, atual)
            continue

        if mov == "suggest":
            suggest_usado, mensagem = suggest(suggest_usado, tesouro, atual)
            continue

        novo_atual = movimentacao(mov, atual)

        if novo_atual == atual and mov in ["up", "down", "left", "right"]:
            mensagem = "Movimentação não permitida!"
        else:
            mensagem = ""

        atual = novo_atual
        markmap(atual, mapa)

if __name__ == "__main__":
    game()
