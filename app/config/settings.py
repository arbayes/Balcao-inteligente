import os
import sys

# Determinar o diretório base corretamente para .exe e desenvolvimento
if getattr(sys, 'frozen', False):
    # Rodando como executável (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Rodando como script Python
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Diretório de dados
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Criar diretórios necessários se não existirem
for directory in [DATA_DIR, 
                  os.path.join(BASE_DIR, 'relatorios'),
                  os.path.join(BASE_DIR, 'backups')]:
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print(f"Erro ao criar diretório {directory}: {e}")

# Caminho do banco de dados
DB_PATH = os.path.join(DATA_DIR, 'gerenciamento.db')