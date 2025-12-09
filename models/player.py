# models/player.py
class Player:
    def __init__(self, pid, addr, nome):
        self.pid = pid
        self.addr = addr  # (ip, porta)
        self.nome = nome
        self.pos = (1, 1)
        self.hint_used = False
        self.suggest_used = False

    def to_dict(self):
        return {
            "pid": self.pid,
            "pos": self.pos,
            "hint_used": self.hint_used,
            "suggest_used": self.suggest_used
        }
    
    def get_human_position(self):
        """Converte posição interna para coordenadas humanas (x, y)"""
        # Assumindo que pos é (i, j) onde i é linha, j é coluna
        i, j = self.pos
        return (j + 1, 3 - i)  # Adaptar conforme necessário