from datetime import datetime

from app.database.connection import get_connection


def criar_tabelas_caixa():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_abertura TIMESTAMP NOT NULL,
            data_fechamento TIMESTAMP,
            saldo_inicial REAL NOT NULL DEFAULT 0,
            saldo_contado REAL,
            saldo_esperado REAL,
            diferenca REAL,
            status TEXT NOT NULL DEFAULT 'ABERTO',
            observacoes TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixa_movimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caixa_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            forma_pagamento TEXT NOT NULL DEFAULT 'Dinheiro',
            origem TEXT DEFAULT 'manual',
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (caixa_id) REFERENCES caixas(id)
        )
    """)
    conn.commit()
    conn.close()


def obter_caixa_aberto():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data_abertura, data_fechamento, saldo_inicial, saldo_contado,
               saldo_esperado, diferenca, status, observacoes
        FROM caixas
        WHERE status = 'ABERTO'
        ORDER BY data_abertura DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def abrir_caixa(saldo_inicial, observacoes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO caixas (data_abertura, saldo_inicial, status, observacoes)
        VALUES (?, ?, 'ABERTO', ?)
    """, (datetime.now(), saldo_inicial, observacoes))
    conn.commit()
    caixa_id = cursor.lastrowid
    conn.close()
    return caixa_id


def fechar_caixa(caixa_id, saldo_contado, saldo_esperado, diferenca, observacoes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE caixas
        SET data_fechamento = ?,
            saldo_contado = ?,
            saldo_esperado = ?,
            diferenca = ?,
            status = 'FECHADO',
            observacoes = ?
        WHERE id = ? AND status = 'ABERTO'
    """, (datetime.now(), saldo_contado, saldo_esperado, diferenca, observacoes, caixa_id))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    return sucesso


def inserir_movimento(caixa_id, tipo, descricao, valor, forma_pagamento="Dinheiro", origem="manual"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO caixa_movimentos
            (caixa_id, tipo, descricao, valor, forma_pagamento, origem, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (caixa_id, tipo, descricao, valor, forma_pagamento, origem, datetime.now()))
    conn.commit()
    movimento_id = cursor.lastrowid
    conn.close()
    return movimento_id


def listar_movimentos(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, caixa_id, tipo, descricao, valor, forma_pagamento, origem, criado_em
        FROM caixa_movimentos
        WHERE caixa_id = ?
        ORDER BY criado_em DESC, id DESC
    """, (caixa_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def listar_caixas(limite=30):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data_abertura, data_fechamento, saldo_inicial, saldo_contado,
               saldo_esperado, diferenca, status, observacoes
        FROM caixas
        ORDER BY data_abertura DESC
        LIMIT ?
    """, (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def obter_caixa(caixa_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data_abertura, data_fechamento, saldo_inicial, saldo_contado,
               saldo_esperado, diferenca, status, observacoes
        FROM caixas
        WHERE id = ?
    """, (caixa_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
