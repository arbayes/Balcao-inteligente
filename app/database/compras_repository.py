"""
REPOSITÓRIO DE COMPRAS DE FORNECEDORES
Gerencia a persistência de compras/pedidos no banco de dados
"""

from typing import List, Optional
from datetime import datetime
from app.database.connection import get_connection
from app.models.compra_fornecedor import CompraFornecedor, ItemCompra


def criar_tabela_compras():
    """Cria as tabelas de compras se não existirem"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Tabela de compras
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras_fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fornecedor_id INTEGER NOT NULL,
                data_pedido TEXT NOT NULL,
                data_entrega_esperada TEXT,
                data_entrega_real TEXT,
                valor_total REAL NOT NULL,
                status TEXT DEFAULT 'PENDENTE',
                forma_pagamento TEXT,
                data_pagamento_esperada TEXT,
                data_pagamento_real TEXT,
                pago INTEGER DEFAULT 0,
                observacoes TEXT,
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
            )
        """)
        
        # Tabela de itens de compra
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_compra_fornecedor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compra_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                produto_nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                FOREIGN KEY (compra_id) REFERENCES compras_fornecedores(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabelas de compras: {e}")
        raise
    finally:
        if conn:
            conn.close()


def inserir_compra(compra: CompraFornecedor) -> int:
    """Insere uma nova compra no banco de dados"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO compras_fornecedores (
                fornecedor_id, data_pedido, data_entrega_esperada, data_entrega_real,
                valor_total, status, forma_pagamento, data_pagamento_esperada,
                data_pagamento_real, pago, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            compra.fornecedor_id,
            compra.data_pedido.isoformat() if compra.data_pedido else datetime.now().isoformat(),
            compra.data_entrega_esperada.isoformat() if compra.data_entrega_esperada else None,
            compra.data_entrega_real.isoformat() if compra.data_entrega_real else None,
            compra.valor_total,
            compra.status,
            compra.forma_pagamento,
            compra.data_pagamento_esperada.isoformat() if compra.data_pagamento_esperada else None,
            compra.data_pagamento_real.isoformat() if compra.data_pagamento_real else None,
            1 if compra.pago else 0,
            compra.observacoes
        ))
        
        compra_id = cursor.lastrowid
        
        # Inserir itens
        for item in compra.itens:
            cursor.execute("""
                INSERT INTO itens_compra_fornecedor (
                    compra_id, produto_id, produto_nome, quantidade, preco_unitario
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                compra_id,
                item.produto_id,
                item.produto_nome,
                item.quantidade,
                item.preco_unitario
            ))
        
        conn.commit()
        return compra_id
    except Exception as e:
        print(f"Erro ao inserir compra: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def obter_compra_por_id(compra_id: int) -> Optional[CompraFornecedor]:
    """Obtém uma compra pelo ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM compras_fornecedores WHERE id = ?", (compra_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Obter itens
        cursor.execute("SELECT * FROM itens_compra_fornecedor WHERE compra_id = ?", (compra_id,))
        itens_rows = cursor.fetchall()
        
        itens = []
        for item_row in itens_rows:
            item = ItemCompra(
                id=item_row[0],
                produto_id=item_row[2],
                produto_nome=item_row[3],
                quantidade=item_row[4],
                preco_unitario=item_row[5]
            )
            itens.append(item)
        
        compra = CompraFornecedor(
            id=row[0],
            fornecedor_id=row[1],
            data_pedido=datetime.fromisoformat(row[2]) if row[2] else None,
            data_entrega_esperada=datetime.fromisoformat(row[3]) if row[3] else None,
            data_entrega_real=datetime.fromisoformat(row[4]) if row[4] else None,
            valor_total=row[5],
            status=row[6],
            forma_pagamento=row[7],
            data_pagamento_esperada=datetime.fromisoformat(row[8]) if row[8] else None,
            data_pagamento_real=datetime.fromisoformat(row[9]) if row[9] else None,
            pago=bool(row[10]),
            observacoes=row[11],
            itens=itens
        )
        
        return compra
    except Exception as e:
        print(f"Erro ao obter compra: {e}")
        return None
    finally:
        if conn:
            conn.close()


def listar_compras_fornecedor(fornecedor_id: int, status: Optional[str] = None) -> List[CompraFornecedor]:
    """Lista compras de um fornecedor"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT id FROM compras_fornecedores WHERE fornecedor_id = ? AND status = ? ORDER BY data_pedido DESC",
                (fornecedor_id, status)
            )
        else:
            cursor.execute(
                "SELECT id FROM compras_fornecedores WHERE fornecedor_id = ? ORDER BY data_pedido DESC",
                (fornecedor_id,)
            )
        
        rows = cursor.fetchall()
        compras = []
        
        for row in rows:
            compra = obter_compra_por_id(row[0])
            if compra:
                compras.append(compra)
        
        return compras
    except Exception as e:
        print(f"Erro ao listar compras: {e}")
        return []
    finally:
        if conn:
            conn.close()


def atualizar_compra(compra: CompraFornecedor) -> bool:
    """Atualiza uma compra existente"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE compras_fornecedores SET
                data_entrega_esperada = ?, data_entrega_real = ?,
                valor_total = ?, status = ?, forma_pagamento = ?,
                data_pagamento_esperada = ?, data_pagamento_real = ?,
                pago = ?, observacoes = ?
            WHERE id = ?
        """, (
            compra.data_entrega_esperada.isoformat() if compra.data_entrega_esperada else None,
            compra.data_entrega_real.isoformat() if compra.data_entrega_real else None,
            compra.valor_total,
            compra.status,
            compra.forma_pagamento,
            compra.data_pagamento_esperada.isoformat() if compra.data_pagamento_esperada else None,
            compra.data_pagamento_real.isoformat() if compra.data_pagamento_real else None,
            1 if compra.pago else 0,
            compra.observacoes,
            compra.id
        ))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar compra: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def deletar_compra(compra_id: int) -> bool:
    """Deleta uma compra"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Deletar itens
        cursor.execute("DELETE FROM itens_compra_fornecedor WHERE compra_id = ?", (compra_id,))
        
        # Deletar compra
        cursor.execute("DELETE FROM compras_fornecedores WHERE id = ?", (compra_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deletar compra: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def obter_compras_pendentes_pagamento() -> List[CompraFornecedor]:
    """Obtém compras com pagamento pendente"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM compras_fornecedores 
            WHERE pago = 0 AND status = 'ENTREGUE'
            ORDER BY data_pagamento_esperada ASC
        """)
        
        rows = cursor.fetchall()
        compras = []
        
        for row in rows:
            compra = obter_compra_por_id(row[0])
            if compra:
                compras.append(compra)
        
        return compras
    except Exception as e:
        print(f"Erro ao obter compras pendentes: {e}")
        return []
    finally:
        if conn:
            conn.close()
