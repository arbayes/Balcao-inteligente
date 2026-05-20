from datetime import datetime
from app.database.connection import get_connection


def criar_tabela_automacoes():
    """Cria a tabela de automacoes do sistema."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS automacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                gatilho TEXT NOT NULL,
                valor_limite REAL DEFAULT 0,
                acao TEXT NOT NULL,
                intervalo_minutos INTEGER DEFAULT 30,
                ativo INTEGER DEFAULT 1,
                ultima_execucao TIMESTAMP,
                ultima_mensagem TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela automacoes: {e}")
        raise
    finally:
        if conn:
            conn.close()


def criar_automacoes_padrao():
    """Cria automacoes iniciais quando ainda nao existe nenhuma regra."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM automacoes")
    total = cursor.fetchone()[0]

    if total == 0:
        automacoes = [
            (
                "Avisar estoque baixo",
                "estoque_baixo",
                5,
                "mostrar_alerta",
                30,
                1,
                "Avisa quando existirem produtos com estoque igual ou abaixo do limite.",
            ),
            (
                "Avisar fiado pendente",
                "fiado_pendente",
                0,
                "mostrar_alerta",
                60,
                1,
                "Avisa quando existirem vendas fiadas pendentes.",
            ),
            (
                "Backup periodico",
                "sempre",
                0,
                "fazer_backup",
                120,
                0,
                "Executa backup periodico quando a regra estiver ativa.",
            ),
        ]
        cursor.executemany("""
            INSERT INTO automacoes
                (nome, gatilho, valor_limite, acao, intervalo_minutos, ativo, ultima_mensagem)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, automacoes)
        conn.commit()

    conn.close()


def listar_automacoes(ativas_apenas=False):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, nome, gatilho, valor_limite, acao, intervalo_minutos,
               ativo, ultima_execucao, ultima_mensagem, criado_em, atualizado_em
        FROM automacoes
    """
    params = []
    if ativas_apenas:
        query += " WHERE ativo = 1"
    query += " ORDER BY ativo DESC, nome ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def obter_automacao(automacao_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, gatilho, valor_limite, acao, intervalo_minutos,
               ativo, ultima_execucao, ultima_mensagem, criado_em, atualizado_em
        FROM automacoes
        WHERE id = ?
    """, (automacao_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def inserir_automacao(nome, gatilho, valor_limite, acao, intervalo_minutos, ativo=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO automacoes
            (nome, gatilho, valor_limite, acao, intervalo_minutos, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, gatilho, valor_limite, acao, intervalo_minutos, 1 if ativo else 0))
    conn.commit()
    automacao_id = cursor.lastrowid
    conn.close()
    return automacao_id


def atualizar_automacao(automacao_id, nome, gatilho, valor_limite, acao, intervalo_minutos, ativo=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE automacoes
        SET nome = ?,
            gatilho = ?,
            valor_limite = ?,
            acao = ?,
            intervalo_minutos = ?,
            ativo = ?,
            atualizado_em = ?
        WHERE id = ?
    """, (
        nome,
        gatilho,
        valor_limite,
        acao,
        intervalo_minutos,
        1 if ativo else 0,
        datetime.now(),
        automacao_id,
    ))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    return sucesso


def alternar_automacao(automacao_id, ativo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE automacoes
        SET ativo = ?, atualizado_em = ?
        WHERE id = ?
    """, (1 if ativo else 0, datetime.now(), automacao_id))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    return sucesso


def registrar_execucao(automacao_id, mensagem):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE automacoes
        SET ultima_execucao = ?,
            ultima_mensagem = ?,
            atualizado_em = ?
        WHERE id = ?
    """, (datetime.now(), mensagem, datetime.now(), automacao_id))
    conn.commit()
    conn.close()


def deletar_automacao(automacao_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM automacoes WHERE id = ?", (automacao_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    return sucesso
