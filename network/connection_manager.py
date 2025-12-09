# network/connection_manager.py
import time
import os

class ConnectionManager:
    def __init__(self):
        self.connections = {}  # nome -> {'rdt': RDT, 'addr': addr, 'player': Player}
        self.online = {}
        self.contatos = {}
    
    def carregar_contatos(self, arquivo="contatos.txt"):
        """Carrega contatos do arquivo"""
        self.contatos.clear()
        if not os.path.exists(arquivo):
            print(f"⚠️ Arquivo {arquivo} não encontrado.")
            return
        
        with open(arquivo, "r") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                
                try:
                    nome, ipporta = linha.split(";")
                    ip, porta = ipporta.split(":")
                    self.contatos[nome] = (ip, int(porta))
                except:
                    print(f"⚠️ Linha inválida: {linha}")
        
        print(f"📋 {len(self.contatos)} contatos carregados")
    
    def adicionar_conexao(self, nome, addr, rdt, player):
        """Adiciona uma nova conexão"""
        self.connections[nome] = {
            'rdt': rdt,
            'addr': addr,
            'player': player,
            'last_active': time.time()
        }
        self.online[nome] = addr
    
    def remover_conexao(self, nome):
        """Remove uma conexão"""
        if nome in self.connections:
            del self.connections[nome]
        if nome in self.online:
            del self.online[nome]
    
    def get_conexao(self, nome):
        """Retorna conexão pelo nome"""
        return self.connections.get(nome)
    
    def get_all_connections(self):
        """Retorna todas as conexões"""
        return list(self.connections.values())
    
    def is_online(self, nome):
        """Verifica se usuário está online"""
        return nome in self.online