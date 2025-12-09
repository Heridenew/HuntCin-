# utils/position_utils.py
def humano_para_interno(x, y):
    """Converte coordenadas humanas para internas"""
    return (3 - y, x - 1)

def interno_para_humano(i, j):
    """Converte coordenadas internas para humanas"""
    return (j + 1, 3 - i)

def validar_posicao(x, y):
    """Valida se posição está dentro do mapa"""
    return 1 <= x <= 3 and 1 <= y <= 3