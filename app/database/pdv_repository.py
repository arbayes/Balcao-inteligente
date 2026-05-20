import json
from datetime import datetime

from app.database.connection import get_connection


def criar_tabelas_pdv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas_pdv (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL DEFAULT 'PRODUTOS',
            cliente_id INTEGER,
            itens TEXT NOT NULL,
            valor_total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            observacoes TEXT,
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def inserir_venda_pdv(tipo, itens, valor_total, forma_pagamento, cliente_id=None, observacoes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vendas_pdv
            (tipo, cliente_id, itens, valor_total, forma_pagamento, observacoes, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        tipo,
        cliente_id,
        json.dumps(itens, ensure_ascii=False),
        valor_total,
        forma_pagamento,
        observacoes,
        datetime.now(),
    ))
    conn.commit()
    venda_id = cursor.lastrowid
    conn.close()
    return venda_id


def listar_vendas_pdv(limite=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo, cliente_id, itens, valor_total, forma_pagamento, observacoes, criado_em
        FROM vendas_pdv
        ORDER BY criado_em DESC, id DESC
        LIMIT ?
    """, (limite,))
    rows = cursor.fetchall()
    conn.close()

    vendas = []
    for row in rows:
        venda = dict(row)
        try:
            venda["itens"] = json.loads(venda["itens"])
        except Exception:
            venda["itens"] = []
        vendas.append(venda)
    return vendas
