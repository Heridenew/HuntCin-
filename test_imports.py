# test_imports.py - VERSÃO CORRIGIDA
print("🧪 Testando importações do projeto HuntCin...")
print("=" * 50)

# Teste 1: Models
try:
    from models import Player, Game
    print("✅ models: Player e Game importados")
except ImportError as e:
    print(f"❌ models: {e}")

# Teste 2: Network
try:
    from network import RDT, ConnectionManager
    print("✅ network: RDT e ConnectionManager importados")
except ImportError as e:
    print(f"❌ network: {e}")

# Teste 3: Services
try:
    from services import GameService
    print("✅ services: GameService importado")
except ImportError as e:
    print(f"❌ services: {e}")

# Teste 4: Utils - CORRIGIDO!
try:
    from utils import humano_para_interno, interno_para_humano
    print("✅ utils: Funções utilitárias importadas")
    
    # Agora testar as constantes do config.py diretamente
    from utils.config import TIMEOUT, SERVER_HOST, SERVER_PORT
    print(f"✅ utils.config: TIMEOUT={TIMEOUT}, SERVER={SERVER_HOST}:{SERVER_PORT}")
    
except ImportError as e:
    print(f"❌ utils: {e}")

# Teste 5: Importações específicas usadas no código real
print("\n🔍 Testando importações específicas dos arquivos principais...")

# Teste para server_udp.py
try:
    from utils.config import SERVER_HOST, SERVER_PORT, BUFFER_SIZE
    print("✅ Importações do server_udp.py: OK")
except ImportError as e:
    print(f"❌ Importações do server_udp.py: {e}")

# Teste para rdt.py
try:
    from utils.config import TIMEOUT, LOSS_PROBABILITY
    print("✅ Importações do rdt.py: OK")
except ImportError as e:
    print(f"❌ Importações do rdt.py: {e}")

print("\n" + "=" * 50)
print("🎯 Todos os testes concluídos!")