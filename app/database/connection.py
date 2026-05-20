import sqlite3
import os
from app.config.settings import DB_PATH

def get_connection():
    """Conecta ao banco de dados SQLite"""
    try:
        # Garantir que o diretório existe
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        print(f"Caminho do banco: {DB_PATH}")
        raise