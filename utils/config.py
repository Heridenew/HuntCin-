# utils/config.py
import os

# Endereço IP do servidor (loopback/localhost)
# "127.0.0.1" indica que o servidor será acessível apenas na própria máquina.
# Em um cenário de rede real, poderia ser substituído por um IP público ou "0.0.0.0" para aceitar conexões de qualquer interface.
SERVER_HOST = "127.0.0.1"

# Porta UDP na qual o servidor escutará as requisições
# Deve ser a mesma porta usada pelo cliente ao enviar dados.
SERVER_PORT = 12345

# Tamanho máximo de cada pacote UDP em bytes
# Valor típico para evitar fragmentação na camada IP.
# O padrão aqui é 1024 bytes (1 KB), conforme exigido no enunciado do projeto.
BUFFER_SIZE = 1024

# Sequência de bytes usada como sinalizador de fim de transmissão de arquivo
# Este marcador é enviado pelo cliente após todos os chunks do arquivo
# e também pelo servidor após devolver o arquivo.
# Deve ser uma sequência improvável de aparecer naturalmente em arquivos binários.
# Usa-se bytes (b"...") para compatibilidade com dados binários.
END_SIGNAL = b"__END__"

TIMEOUT = 2.0             # Tempo em segundos para timeout
LOSS_PROBABILITY = float(os.getenv("LOSS_PROBABILITY", 0.2))  # 20% por padrão