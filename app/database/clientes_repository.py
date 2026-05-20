from app.database.connection import get_connection
from app.models.cliente import Cliente
from datetime import datetime

def criar_tabela_clientes():
    """Cria a tabela de clientes com campos expandidos."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                ativo INTEGER DEFAULT 1,
                vip INTEGER DEFAULT 0,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_ultima_compra TIMESTAMP,
                valor_total_gasto REAL DEFAULT 0.0
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela clientes: {e}")
        raise
    finally:
        if conn:
            conn.close()

def inserir_cliente(cliente: Cliente):
    """Insere um novo cliente no banco de dados."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes (nome, cpf, telefone, email, endereco, ativo, vip, data_cadastro, valor_total_gasto) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente.nome,
        cliente.cpf,
        cliente.telefone,
        cliente.email,
        cliente.endereco,
        1 if cliente.ativo else 0,
        1 if cliente.vip else 0,
        cliente.data_cadastro,
        cliente.valor_total_gasto
    ))
    conn.commit()
    conn.close()

def listar_clientes(busca: str = None, filtro_por: str = None):
    """
    Lista clientes ativos com busca avançada por múltiplos parâmetros.
    
    Args:
        busca (str, optional): Termo de busca
        filtro_por (str, optional): Campo para filtrar
    
    Returns:
        list[Cliente]: Lista de clientes que correspondem aos critérios
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, nome, cpf, telefone, email, endereco, ativo, vip, data_cadastro, data_ultima_compra, valor_total_gasto FROM clientes WHERE ativo = 1"
    params = []
    
    if busca:
        busca_formatado = f"%{busca}%"
        
        if filtro_por and filtro_por.lower() in ['nome', 'cpf', 'telefone', 'email']:
            query += f" AND {filtro_por} LIKE ?"
            params.append(busca_formatado)
        else:
            query += " AND (nome LIKE ? OR cpf LIKE ? OR telefone LIKE ? OR email LIKE ?)"
            params = [busca_formatado, busca_formatado, busca_formatado, busca_formatado]
    
    query += " ORDER BY vip DESC, data_ultima_compra DESC, nome ASC"
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    
    clientes = []
    for resultado in resultados:
        cliente = Cliente(
            id=resultado[0],
            nome=resultado[1],
            cpf=resultado[2],
            telefone=resultado[3],
            email=resultado[4],
            endereco=resultado[5],
            ativo=bool(resultado[6]),
            vip=bool(resultado[7]),
            data_cadastro=datetime.fromisoformat(resultado[8]) if resultado[8] else None,
            data_ultima_compra=datetime.fromisoformat(resultado[9]) if resultado[9] else None,
            valor_total_gasto=resultado[10]
        )
        clientes.append(cliente)
    
    return clientes


def atualizar_cliente(cliente_id: int, **kwargs):
    """
    Atualiza dados do cliente dinamicamente.
    
    Args:
        cliente_id (int): ID do cliente
        **kwargs: Campos a atualizar (nome, cpf, telefone, email, endereco, vip)
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    campos_permitidos = {'nome', 'cpf', 'telefone', 'email', 'endereco', 'vip'}
    campos_atualizacao = {k: v for k, v in kwargs.items() if k in campos_permitidos}
    
    if not campos_atualizacao:
        conn.close()
        return False
    
    updates = []
    params = []
    
    for campo, valor in campos_atualizacao.items():
        updates.append(f"{campo} = ?")
        if campo == 'vip':
            params.append(1 if valor else 0)
        else:
            params.append(valor)
    
    params.append(cliente_id)
    
    query = f"UPDATE clientes SET {', '.join(updates)} WHERE id = ? AND ativo = 1"
    
    cursor.execute(query, params)
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def desativar_cliente(cliente_id: int):
    """
    Desativa um cliente (soft delete).
    
    Args:
        cliente_id (int): ID do cliente a desativar
    
    Returns:
        bool: True se desativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE clientes SET ativo = 0 WHERE id = ? AND ativo = 1", (cliente_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def reativar_cliente(cliente_id: int):
    """
    Reativa um cliente que foi desativado.
    
    Args:
        cliente_id (int): ID do cliente a reativar
    
    Returns:
        bool: True se reativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE clientes SET ativo = 1 WHERE id = ? AND ativo = 0", (cliente_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def obter_cliente_por_id(cliente_id: int):
    """
    Obtém um cliente específico pelo ID (apenas se ativo).
    
    Args:
        cliente_id (int): ID do cliente
    
    Returns:
        Cliente: Objeto cliente ou None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, cpf, telefone, email, endereco, ativo, vip, data_cadastro, data_ultima_compra, valor_total_gasto FROM clientes WHERE id = ? AND ativo = 1",
        (cliente_id,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return Cliente(
            id=resultado[0],
            nome=resultado[1],
            cpf=resultado[2],
            telefone=resultado[3],
            email=resultado[4],
            endereco=resultado[5],
            ativo=bool(resultado[6]),
            vip=bool(resultado[7]),
            data_cadastro=datetime.fromisoformat(resultado[8]) if resultado[8] else None,
            data_ultima_compra=datetime.fromisoformat(resultado[9]) if resultado[9] else None,
            valor_total_gasto=resultado[10]
        )
    return None


def obter_clientes_vip():
    """Retorna lista de clientes VIP ordenados por valor gasto."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nome, cpf, telefone, email, endereco, ativo, vip, data_cadastro, data_ultima_compra, valor_total_gasto 
        FROM clientes 
        WHERE ativo = 1 AND vip = 1
        ORDER BY valor_total_gasto DESC
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    clientes = []
    for resultado in resultados:
        cliente = Cliente(
            id=resultado[0],
            nome=resultado[1],
            cpf=resultado[2],
            telefone=resultado[3],
            email=resultado[4],
            endereco=resultado[5],
            ativo=bool(resultado[6]),
            vip=bool(resultado[7]),
            data_cadastro=datetime.fromisoformat(resultado[8]) if resultado[8] else None,
            data_ultima_compra=datetime.fromisoformat(resultado[9]) if resultado[9] else None,
            valor_total_gasto=resultado[10]
        )
        clientes.append(cliente)
    
    return clientes


def obter_clientes_inativos_desde_dias(dias: int = 30):
    """Retorna clientes inativos (sem compras) há N dias."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"""
        SELECT id, nome, cpf, telefone, email, endereco, ativo, vip, data_cadastro, data_ultima_compra, valor_total_gasto 
        FROM clientes 
        WHERE ativo = 1 
        AND (data_ultima_compra IS NULL OR datetime(data_ultima_compra) < datetime('now', '-{dias} days'))
        ORDER BY data_ultima_compra ASC
    """)
    resultados = cursor.fetchall()
    conn.close()
    
    clientes = []
    for resultado in resultados:
        cliente = Cliente(
            id=resultado[0],
            nome=resultado[1],
            cpf=resultado[2],
            telefone=resultado[3],
            email=resultado[4],
            endereco=resultado[5],
            ativo=bool(resultado[6]),
            vip=bool(resultado[7]),
            data_cadastro=datetime.fromisoformat(resultado[8]) if resultado[8] else None,
            data_ultima_compra=datetime.fromisoformat(resultado[9]) if resultado[9] else None,
            valor_total_gasto=resultado[10]
        )
        clientes.append(cliente)
    
    return clientes


def atualizar_valor_gasto(cliente_id: int, valor: float):
    """Atualiza o valor total gasto e data última compra."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE clientes 
        SET valor_total_gasto = valor_total_gasto + ?, 
            data_ultima_compra = CURRENT_TIMESTAMP
        WHERE id = ? AND ativo = 1
    """, (valor, cliente_id))
    
    conn.commit()
    conn.close()