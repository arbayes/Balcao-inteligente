"""
Otimização de Banco de Dados - Índices e Cache
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from functools import lru_cache
import hashlib

class DatabaseOptimizer:
    """Otimiza queries e adiciona índices"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.cache: Dict[str, Any] = {}
        self.cache_hash: Dict[str, str] = {}
    
    def criar_indices(self):
        """Cria índices para colunas frequentes"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Índices para tabela clientes
            indices_clientes = [
                "CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)",
                "CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes(cpf)",
                "CREATE INDEX IF NOT EXISTS idx_clientes_data ON clientes(data_cadastro)"
            ]
            
            # Índices para tabela estoque
            indices_estoque = [
                "CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)",
                "CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)",
                "CREATE INDEX IF NOT EXISTS idx_produtos_quantidade ON produtos(quantidade)"
            ]
            
            # Índices para tabela vendas_fiadas
            indices_vendas = [
                "CREATE INDEX IF NOT EXISTS idx_vendas_cliente ON vendas_fiadas(cliente_id)",
                "CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas_fiadas(data_venda)",
                "CREATE INDEX IF NOT EXISTS idx_vendas_status ON vendas_fiadas(status)"
            ]
            
            # Índices para tabela compras
            indices_compras = [
                "CREATE INDEX IF NOT EXISTS idx_compras_fornecedor ON compras(fornecedor_id)",
                "CREATE INDEX IF NOT EXISTS idx_compras_data ON compras(data_compra)",
                "CREATE INDEX IF NOT EXISTS idx_compras_status ON compras(status)"
            ]
            
            todos_indices = indices_clientes + indices_estoque + indices_vendas + indices_compras
            
            for indice in todos_indices:
                try:
                    cursor.execute(indice)
                    print(f"✅ {indice.split('ON')[1].strip()}")
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        print(f"⚠️ Erro ao criar índice: {e}")
            
            # Analisar table stats para otimização
            cursor.execute("ANALYZE")
            
            conn.commit()
            conn.close()
            print("✅ Índices criados com sucesso!")
            return True
        
        except Exception as e:
            print(f"❌ Erro ao criar índices: {e}")
            return False
    
    def otimizar_conexao(self, conn: sqlite3.Connection):
        """Otimiza configurações da conexão SQLite"""
        cursor = conn.cursor()
        
        # Ativar WAL mode para melhor concorrência
        cursor.execute("PRAGMA journal_mode=WAL")
        
        # Aumentar cache
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        
        # Sincronização normal (mais rápido, menos seguro)
        cursor.execute("PRAGMA synchronous=NORMAL")
        
        # Aumentar tamanho de page
        cursor.execute("PRAGMA page_size=4096")
        
        # Foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        
        conn.commit()
    
    def cache_resultado(self, chave: str, dados: Any) -> None:
        """Armazena resultado em cache"""
        self.cache[chave] = dados
        # Hash para invalidação
        self.cache_hash[chave] = hashlib.md5(str(dados).encode()).hexdigest()
    
    def obter_cache(self, chave: str) -> Optional[Any]:
        """Recupera resultado do cache"""
        return self.cache.get(chave)
    
    def invalidar_cache(self, chave: str = None):
        """Invalida cache"""
        if chave:
            self.cache.pop(chave, None)
            self.cache_hash.pop(chave, None)
        else:
            self.cache.clear()
            self.cache_hash.clear()
    
    def criar_view_relatorios(self):
        """Cria views SQL para relatórios rápidos"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            views = [
                """
                CREATE VIEW IF NOT EXISTS vw_vendas_por_mes AS
                SELECT 
                    strftime('%Y-%m', data_venda) as mes,
                    COUNT(*) as quantidade,
                    SUM(valor_total) as total
                FROM vendas_fiadas
                GROUP BY mes
                ORDER BY mes DESC
                """,
                
                """
                CREATE VIEW IF NOT EXISTS vw_clientes_com_divida AS
                SELECT 
                    c.id,
                    c.nome,
                    COUNT(vf.id) as quantidade_vendas,
                    SUM(vf.valor_total) as divida_total
                FROM clientes c
                LEFT JOIN vendas_fiadas vf ON c.id = vf.cliente_id AND vf.status != 'PAGO'
                GROUP BY c.id
                HAVING divida_total > 0
                ORDER BY divida_total DESC
                """,
                
                """
                CREATE VIEW IF NOT EXISTS vw_estoque_baixo AS
                SELECT 
                    id,
                    nome,
                    categoria,
                    quantidade,
                    preco_venda,
                    quantidade * preco_venda as valor_total
                FROM produtos
                WHERE quantidade < 5
                ORDER BY quantidade ASC
                """,
                
                """
                CREATE VIEW IF NOT EXISTS vw_compras_pendentes AS
                SELECT 
                    c.id,
                    f.nome as fornecedor,
                    c.data_compra,
                    c.data_entrega_esperada,
                    c.valor_total,
                    c.status,
                    c.pago
                FROM compras c
                JOIN fornecedores f ON c.fornecedor_id = f.id
                WHERE c.status = 'PENDING' OR c.pago = 0
                ORDER BY c.data_entrega_esperada ASC
                """
            ]
            
            for view in views:
                cursor.execute(view)
            
            conn.commit()
            conn.close()
            print("✅ Views de relatório criadas!")
            return True
        
        except Exception as e:
            print(f"❌ Erro ao criar views: {e}")
            return False
    
    def analisar_performance(self) -> Dict[str, Any]:
        """Analisa performance do banco"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            stats = {}
            
            # Tamanho do banco
            tamanho_bytes = self.db_path.stat().st_size
            stats['tamanho_db_mb'] = round(tamanho_bytes / (1024 * 1024), 2)
            
            # Contar registros por tabela
            tabelas = ['clientes', 'produtos', 'vendas_fiadas', 'compras', 'fornecedores']
            stats['registros'] = {}
            
            for tabela in tabelas:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                    count = cursor.fetchone()[0]
                    stats['registros'][tabela] = count
                except:
                    pass
            
            # Verificar índices
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
            stats['total_indices'] = len(cursor.fetchall())
            
            conn.close()
            return stats
        
        except Exception as e:
            print(f"Erro ao analisar performance: {e}")
            return {}


# Singleton global
_db_optimizer = None

def get_db_optimizer(db_path: str = None) -> DatabaseOptimizer:
    """Retorna instância global do otimizador"""
    global _db_optimizer
    
    if _db_optimizer is None:
        if db_path is None:
            from app.config.settings import DB_PATH
            db_path = str(DB_PATH)
        
        _db_optimizer = DatabaseOptimizer(db_path)
    
    return _db_optimizer
