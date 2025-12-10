"""
Teste automatizado básico: 1 servidor + 2 clientes.
Faz login automático (teste1 @5221 e teste2 @6169) e PARA
na fase de comandos para você digitar manualmente em cada terminal.

Como usar:
  python test_automate.py

Pré-requisitos:
- Arquivo contatos.txt deve conter os nomes/ports usados abaixo.
- SERVER_HOST/PORT em utils.config devem estar acessíveis (127.0.0.1:12345).
"""

import subprocess
import sys
import threading
import time
import os
from pathlib import Path

# Clientes de teste: (nome, porta)
CLIENTS = [
    ("Livia", "5221"),
    ("Edenn", "6169"),
]

def stream_pipe(src, prefix):
    """Lê stdout/err de um processo e imprime com prefixo (uso em Unix)."""
    for line in iter(src.readline, b""):
        try:
            print(f"{prefix} {line.decode(errors='ignore').rstrip()}")
        except Exception:
            pass


def start_process(cmd, prefix):
    """
    Inicia processo.
    - No Windows: abre nova janela de console, sem redirecionar stdin/stdout (para digitar diretamente).
    - No Unix: mantém pipes e imprime no console principal.
    """
    if os.name == "nt":
        return subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=False,
        )
        if proc.stdout:
            t = threading.Thread(target=stream_pipe, args=(proc.stdout, prefix), daemon=True)
            t.start()
        return proc


def feed_inputs(proc, inputs, delay_between=1.0):
    """Envia linhas ao stdin do processo com pequenos delays."""
    for line in inputs:
        if proc.poll() is not None:
            return
        try:
            proc.stdin.write((line + "\n").encode())
            proc.stdin.flush()
        except Exception:
            return
        time.sleep(delay_between)


def main():
    root = Path(__file__).parent
    py = sys.executable

    # 1) Servidor em nova janela
    server_cmd = [py, str(root / "server_udp.py")]
    server = start_process(server_cmd, "[SERVER]")
    time.sleep(2.0)  # dar tempo para bind

    # 2) Clientes em novas janelas, com porta/nome via args
    clients = []
    for idx, (nome, porta) in enumerate(CLIENTS):
        client_cmd = [
            py,
            str(root / "client_udp.py"),
            "--port",
            porta,
            "--name",
            nome,
        ]
        proc = start_process(client_cmd, f"[CLIENT{idx+1}]")
        clients.append(proc)
        time.sleep(1.0)

    # 3) Entrar na fase de comandos manual: deixe abertos para digitar
    print("\n⚠️  Agora digite os comandos manualmente nos terminais dos clientes.")
    print("   Exemplos: move up/down/left/right, hint, suggest, logout")
    print("   Pressione Ctrl+C aqui quando terminar os testes.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando processos...")
        for proc in clients:
            if proc.poll() is None:
                proc.terminate()
        if server.poll() is None:
            server.terminate()
        for proc in clients + [server]:
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:
                    proc.kill()
                except Exception:
                    pass


if __name__ == "__main__":
    print("🏁 Iniciando teste automatizado: 1 servidor + 2 clientes")
    main()
    print("✅ Teste automatizado finalizado")

