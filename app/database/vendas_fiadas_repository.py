import json
from datetime import datetime
from app.database.connection import get_connection
from app.models.venda_fiada import VendaFiada

def criar_tabela_vendas_fiadas():
    """Cria a tabela de vendas fiadas."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas_fiadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                produtos TEXT NOT NULL,
                valor_total REAL NOT NULL,
                status TEXT DEFAULT 'PENDENTE',
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_pagamento TIMESTAMP,
                notas TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela vendas_fiadas: {e}")
        raise
    finally:
        if conn:
            conn.close()

def inserir_venda_fiada(venda: VendaFiada):
    """Insere uma nova venda fiada."""
    conn = get_connection()
    cursor = conn.cursor()
    
    produtos_json = json.dumps(venda.produtos)
    
    cursor.execute("""
        INSERT INTO vendas_fiadas (cliente_id, produtos, valor_total, status, data_venda, notas)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        venda.cliente_id,
        produtos_json,
        venda.valor_total,
        venda.status,
        venda.data_venda,
        venda.notas
    ))
    conn.commit()
    conn.close()

def listar_vendas_fiadas_por_cliente(cliente_id: int) -> list:
    """Lista todas as vendas fiadas de um cliente."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, cliente_id, produtos, valor_total, status, data_venda, data_pagamento, notas
        FROM vendas_fiadas
        WHERE cliente_id = ?
        ORDER BY data_venda DESC
    """, (cliente_id,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    vendas = []
    for row in resultados:
        venda = VendaFiada(
            id=row[0],
            cliente_id=row[1],
            produtos=json.loads(row[2]),
            valor_total=row[3],
            status=row[4],
            data_venda=row[5],
            data_pagamento=row[6],
            notas=row[7]
        )
        vendas.append(venda)
    
    return vendas

def listar_vendas_fiadas_pendentes() -> list:
    """Lista todas as vendas fiadas pendentes (não pagas)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, cliente_id, produtos, valor_total, status, data_venda, data_pagamento, notas
        FROM vendas_fiadas
        WHERE status IN ('PENDENTE', 'PARCIAL', 'INADIMPLENTE')
        ORDER BY data_venda DESC
    """)
    
    resultados = cursor.fetchall()
    conn.close()
    
    vendas = []
    for row in resultados:
        venda = VendaFiada(
            id=row[0],
            cliente_id=row[1],
            produtos=json.loads(row[2]),
            valor_total=row[3],
            status=row[4],
            data_venda=row[5],
            data_pagamento=row[6],
            notas=row[7]
        )
        vendas.append(venda)
    
    return vendas

def calcular_divida_cliente(cliente_id: int) -> dict:
    """Calcula a dívida total de um cliente."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(valor_total), COUNT(*), GROUP_CONCAT(status)
        FROM vendas_fiadas
        WHERE cliente_id = ? AND status IN ('PENDENTE', 'PARCIAL', 'INADIMPLENTE')
    """, (cliente_id,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    divida_total = resultado[0] or 0
    quantidade_vendas = resultado[1] or 0
    statuses = (resultado[2] or "").split(",")
    
    return {
        "divida_total": divida_total,
        "quantidade_vendas": quantidade_vendas,
        "inadimplente": "INADIMPLENTE" in statuses
    }

def atualizar_status_venda(venda_id: int, novo_status: str, data_pagamento: datetime = None):
    """Atualiza o status de uma venda fiada."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE vendas_fiadas
        SET status = ?, data_pagamento = ?
        WHERE id = ?
    """, (novo_status, data_pagamento, venda_id))
    
    conn.commit()
    conn.close()

def deletar_venda_fiada(venda_id: int):
    """Deleta uma venda fiada."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM vendas_fiadas WHERE id = ?", (venda_id,))
    conn.commit()
    conn.close()

def obter_venda_fiada(venda_id: int) -> VendaFiada:
    """Obtém uma venda fiada específica."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, cliente_id, produtos, valor_total, status, data_venda, data_pagamento, notas
        FROM vendas_fiadas
        WHERE id = ?
    """, (venda_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return VendaFiada(
            id=row[0],
            cliente_id=row[1],
            produtos=json.loads(row[2]),
            valor_total=row[3],
            status=row[4],
            data_venda=row[5],
            data_pagamento=row[6],
            notas=row[7]
        )
    return None

def atualizar_venda_fiada(venda_id: int, **kwargs):
    """Atualiza campos de uma venda fiada."""
    conn = get_connection()
    cursor = conn.cursor()
    
    campos = []
    valores = []
    
    if 'status' in kwargs:
        campos.append("status = ?")
        valores.append(kwargs['status'])
    
    if 'notas' in kwargs:
        campos.append("notas = ?")
        valores.append(kwargs['notas'])
    
    if 'data_pagamento' in kwargs:
        campos.append("data_pagamento = ?")
        valores.append(kwargs['data_pagamento'])
    
    if campos:
        valores.append(venda_id)
        query = f"UPDATE vendas_fiadas SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(query, valores)
        conn.commit()
    
    conn.close()
