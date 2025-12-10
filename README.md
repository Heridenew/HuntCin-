# 🗺️ HuntCin -- Jogo Multiplayer via UDP com RDT 3.0

**HuntCin** é um jogo multiplayer de caça ao tesouro implementado em
Python usando **UDP confiável (RDT 3.0)**.\
O projeto implementa envio confiável de pacotes, controle de conexão,
gerenciamento de jogadores, lógica de jogo por rodadas e comunicação
cliente-servidor.

------------------------------------------------------------------------

## 📌 Funcionalidades Principais

### ✔️ Protocolo RDT (Reliable Data Transfer)

-   Envio e recepção confiável via **UDP**
-   ACK, reenvio, verificação de checksum
-   Threads independentes de recepção
-   Tratamento de timeouts

### ✔️ Servidor UDP com controle de jogadores

-   Login com validação
-   Gerenciamento de conexões
-   Rodadas de jogo
-   Sistema de timeout
-   Broadcast para todos os jogadores
-   Suporte a desconexões

### ✔️ Cliente interativo

-   Interface no terminal
-   Recepção assíncrona de mensagens
-   Fila não bloqueante (queue)
-   Comandos:
    -   `move up/down/left/right`
    -   `hint`
    -   `suggest`
    -   `logout`

### ✔️ Jogo de Caça ao Tesouro

-   Mapa interno
-   Movimentação por turnos
-   Dicas e sugestões
-   Vitória ao encontrar o tesouro
-   Reinício automático

------------------------------------------------------------------------

## 🗂️ Estrutura do Projeto
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


------------------------------------------------------------------------

## 🚀 Como Executar

### 1️⃣ Iniciar o servidor

``` bash
python main.py server
```

### 2️⃣ Iniciar o cliente

``` bash
python main.py client
```

Ou usando argumentos:

``` bash
python client_udp.py --port 5001 --name João
```

Cada cliente deve usar **porta diferente**.

------------------------------------------------------------------------

## 🎮 Comandos do Jogo

  Comando        Ação
  -------------- --------------------
  `move up`      Move para cima
  `move down`    Move para baixo
  `move left`    Move para esquerda
  `move right`   Move para direita
  `hint`         Solicita dica
  `suggest`      Faz sugestão
  `logout`       Sai do jogo

------------------------------------------------------------------------

## 📡 Protocolo RDT

O projeto implementa: - Pacotes numerados 0/1\
- ACK explícito\
- Checksum\
- Timeout + reenvio\
- Parsing correto no cliente e servidor

------------------------------------------------------------------------

## 👥 Multijogador

-   Múltiplos clientes simultâneos\
-   Cada jogador possui PID, nome, posição e sua própria conexão RDT\
-   Broadcasts automáticos do servidor

------------------------------------------------------------------------

## 🔧 Dependências

Todas são da biblioteca padrão Python: - socket\
- threading\
- queue\
- logging\
- time\
- re

------------------------------------------------------------------------

## 📄 contatos.txt

Arquivo de contatos no formato:

    nome;IP:PORTA

------------------------------------------------------------------------

## 🏆 Objetivo

Mover-se pelo mapa e **encontrar o tesouro antes dos outros**!

------------------------------------------------------------------------

## 👥 Participantes

- **Alexsandro José da Silva** — <ajs6@cin.ufpe.br>  
- **João Henrique dos Santos Silva** — <jhss2@cin.ufpe.br>  
- **Edenn Weslley dos Santos Silva** — <ewss@cin.ufpe.br>

------------------------------------------------------------------------

## 📜 Licença

Projeto acadêmico --- uso livre para fins educacionais.
