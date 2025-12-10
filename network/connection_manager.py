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
    
    def validar_login(self, nome, addr):
        """Valida credenciais de login - MÉTODO QUE FALTAVA"""
        if nome not in self.contatos:
            return False, f"Nome '{nome}' não cadastrado"
        
        if nome in self.online:
            return False, f"Usuário '{nome}' já está online"
        
        # Verificar porta
        ip_cliente, porta_cliente = addr
        ip_cadastrado, porta_cadastrada = self.contatos[nome]
        
        if str(porta_cliente) != str(porta_cadastrada):
            return False, f"Porta incorreta. Esperada: {porta_cadastrada}, Recebida: {porta_cliente}"
        
        return True, "Login válido"
    
    def adicionar_conexao(self, nome, addr, rdt, player):
        """Adiciona uma nova conexão"""
        self.connections[nome] = {
            'rdt': rdt,
            'addr': addr,
            'player': player,
            'last_active': time.time()
        }
        self.online[nome] = addr
        print(f"✅ {nome} conectado de {addr} (PID: {player.pid})")
    
    def remover_conexao(self, nome):
        """Remove uma conexão"""
        if nome in self.connections:
            del self.connections[nome]
        if nome in self.online:
            del self.online[nome]
        print(f"❌ {nome} desconectado")
    
    def get_conexao(self, nome):
        """Retorna conexão pelo nome"""
        return self.connections.get(nome)
    
    def get_all_connections(self):
        """Retorna todas as conexões"""
        return list(self.connections.values())
    
    def is_online(self, nome):
        """Verifica se usuário está online"""
        return nome in self.online
    
    def get_jogador_por_addr(self, addr):
        """Retorna jogador pelo endereço - MÉTODO QUE FALTAVA"""
        for nome, conn in self.connections.items():
            if conn['addr'] == addr:
                return nome, conn
        return None, None
    
    def get_qtd_jogadores(self):
        """Retorna quantidade de jogadores conectados - MÉTODO QUE FALTAVA"""
        return len(self.connections)
    
    def broadcast(self, mensagem, excluir=None):
        """Envia mensagem para todos os jogadores conectados - MÉTODO QUE FALTAVA"""
        for nome, conn in self.connections.items():
            if excluir and nome == excluir:
                continue
            try:
                conn['rdt'].send(mensagem.encode())
            except ConnectionResetError as e:
                # Cliente caiu; remover para não travar envios
                print(f"❌ Broadcast falhou para {nome} (conexão resetada). Removendo jogador.")
                try:
                    # remover_jogador pode depender do service, então aqui removemos conexão básica
                    self.remover_conexao(nome)
                except Exception:
                    pass
            except Exception as e:
                print(f"❌ Erro enviando broadcast para {nome}: {e}")