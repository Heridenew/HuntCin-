# player.py

class Player:
    def __init__(self, pid, conn, addr, nome):
        self.pid = pid
        self.conn = conn
        self.addr = addr
        self.nome = nome
        self.pos = (1, 1)


    def to_dict(self):
        return {
            "pid": self.pid,
            "pos": self.pos,
            "hint_used": self.hint_used,
            "suggest_used": self.suggest_used
        }
