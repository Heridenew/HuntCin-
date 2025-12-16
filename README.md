# 🗺️ HuntCin -- Jogo Multiplayer via UDP com RDT 3.0

**HuntCin** é um jogo multiplayer de caça ao tesouro implementado em Python usando **UDP confiável (RDT 3.0)**. O projeto implementa envio confiável de pacotes, controle de conexão, gerenciamento de jogadores, lógica de jogo por rodadas e comunicação cliente-servidor.

------------------------------------------------------------------------

## 📌 Funcionalidades Principais

###  Protocolo RDT (Reliable Data Transfer)

-   Envio e recepção confiável via **UDP**
-   ACK, reenvio, verificação de checksum
-   Threads independentes de recepção
-   Tratamento de timeouts

###  Servidor UDP com controle de jogadores

-   Login com validação
-   Gerenciamento de conexões
-   Rodadas de jogo
-   Sistema de timeout
-   Broadcast para todos os jogadores
-   Suporte a desconexões

###  Cliente interativo

-   Interface no terminal
-   Recepção assíncrona de mensagens
-   Comandos:
    -   `move up/down/left/right`
    -   `hint`
    -   `suggest`
    -   `logout`

###  Jogo de Caça ao Tesouro

-   Mapa interno
-   Movimentação por turnos
-   Dicas e sugestões
-   Vitória ao encontrar o tesouro
-   Reinício automático

------------------------------------------------------------------------

##  Estrutura do Projeto

```
.
│   client_udp.py
│   contatos.txt
│   main.py
│   README.md
│   server_udp.py
│   __init__.py
│
├───models
│   │   game.py
│   │   player.py
│   │   __init__.py
│
├───network
│   │   connection_manager.py
│   │   rdt.py
│   │   __init__.py
│
├───services
│   │   game_services.py
│   │   __init__.py
│
└───utils
    │   config.py
    │   positions_utils.py
    │   __init__.py
```

------------------------------------------------------------------------

##  Como Executar

### 1️ Iniciar o servidor (em um terminal)

```bash
python main.py server
```

### 2️ Iniciar os clientes (em terminais separados)

**Cliente 1:**
```bash
python main.py client
```

**Cliente 2:**
```bash
python main.py client
```

> **Importante:** Cada cliente deve usar **uma porta diferente** e seu nome deve estar cadastrado no arquivo `contatos.txt`

------------------------------------------------------------------------

##  Pré-requisitos

1. **Python 3.8 ou superior**
2. **Arquivo `contatos.txt`** configurado com os jogadores
3. **Pelo menos 2 terminais abertos** (1 para servidor, 1+ para clientes)

### Configurar o arquivo `contatos.txt`:
```
João;127.0.0.1:5001
Maria;127.0.0.1:5002
Pedro;127.0.0.1:5003
```

------------------------------------------------------------------------

## 🎮 Comandos do Jogo

| Comando        | Ação                                 |
|----------------|---------------------------------------|
| `move up`      | Move para cima                       |
| `move down`    | Move para baixo                      |
| `move left`    | Move para esquerda                   |
| `move right`   | Move para direita                    |
| `hint`         | Solicita dica sobre direção do tesouro |
| `suggest`      | Recebe sugestão específica (ex: "move up 2 casas") |
| `logout`       | Sai do jogo                          |

------------------------------------------------------------------------

##  Protocolo RDT

O projeto implementa:

-   Pacotes numerados 0/1
-   ACK explícito
-   Checksum MD5
-   Timeout + reenvio automático
-   Parsing correto no cliente e servidor

------------------------------------------------------------------------

##  Multijogador

-   Múltiplos clientes simultâneos
-   Cada jogador possui PID, nome, posição e sua própria conexão RDT
-   Broadcasts automáticos do servidor
-   Rodadas simultâneas com timeout
-   Sistema de pontuação persistente

------------------------------------------------------------------------

##  Dependências

Todas são da biblioteca padrão Python:

-   socket
-   threading
-   queue
-   logging
-   time
-   re
-   random

------------------------------------------------------------------------

##  contatos.txt

Arquivo de contatos no formato:

```
nome;IP:PORTA
```

Exemplo:
```
Joao;127.0.0.1:5001
Maria;127.0.0.1:5002
```

------------------------------------------------------------------------

##  Objetivo do Jogo

Mover-se pelo mapa 3x3 e **encontrar o tesouro antes dos outros**!
O tesouro é posicionado aleatoriamente a cada partida (exceto na posição inicial).

------------------------------------------------------------------------

## 👥 Participantes

-   **Alexsandro José da Silva** --- <ajs6@cin.ufpe.br>
-   **Edenn Weslley dos Santos Silva** --- <ewss@cin.ufpe.br>

------------------------------------------------------------------------

## 📜 Licença

Projeto acadêmico --- uso livre para fins educacionais.
