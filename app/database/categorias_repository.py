"""
REPOSITÓRIO DE CATEGORIAS
Acesso a dados de categorias de produtos
"""

from app.database.connection import get_connection


def criar_tabela_categorias():
    """Cria a tabela de categorias se não existir"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                margem_alvo REAL,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1
            )
        """)
        cursor.execute("PRAGMA table_info(categorias)")
        colunas = [row[1] for row in cursor.fetchall()]
        if "margem_alvo" not in colunas:
            cursor.execute("ALTER TABLE categorias ADD COLUMN margem_alvo REAL")
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela categorias: {e}")
        raise
    finally:
        if conn:
            conn.close()


def inserir_categoria(nome: str, descricao: str = None, margem_alvo: float = None) -> int:
    """
    Insere uma nova categoria.
    
    Args:
        nome (str): Nome da categoria
        descricao (str, optional): Descrição da categoria
    
    Returns:
        int: ID da categoria inserida
    
    Raises:
        ValueError: Se a categoria já existe
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO categorias (nome, descricao, margem_alvo) VALUES (?, ?, ?)",
            (nome.strip(), descricao.strip() if descricao else None, margem_alvo)
        )
        conn.commit()
        categoria_id = cursor.lastrowid
        conn.close()
        return categoria_id
    except Exception as e:
        conn.close()
        raise ValueError(f"Erro ao inserir categoria: {str(e)}")


def listar_categorias(ativas=True) -> list:
    """
    Lista categorias.
    
    Args:
        ativas (bool): Se True, lista apenas categorias ativas
    
    Returns:
        list: Lista de categorias com id, nome, descricao, data_criacao, ativo
    
    Exemplo:
        categorias = listar_categorias()
        # [{'id': 1, 'nome': 'Carnes', 'descricao': '...', ...}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if ativas:
        cursor.execute(
            "SELECT id, nome, descricao, margem_alvo, data_criacao, ativo FROM categorias WHERE ativo = 1 ORDER BY nome ASC"
        )
    else:
        cursor.execute(
            "SELECT id, nome, descricao, margem_alvo, data_criacao, ativo FROM categorias ORDER BY nome ASC"
        )
    
    resultados = cursor.fetchall()
    conn.close()
    
    categorias = []
    for resultado in resultados:
        categorias.append({
            "id": resultado[0],
            "nome": resultado[1],
            "descricao": resultado[2],
            "margem_alvo": resultado[3],
            "data_criacao": resultado[4],
            "ativo": resultado[5]
        })
    
    return categorias


def obter_categoria_por_id(categoria_id: int) -> dict:
    """
    Obtém uma categoria pelo ID.
    
    Args:
        categoria_id (int): ID da categoria
    
    Returns:
        dict: Dados da categoria ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, descricao, margem_alvo, data_criacao, ativo FROM categorias WHERE id = ?",
        (categoria_id,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            "id": resultado[0],
            "nome": resultado[1],
            "descricao": resultado[2],
            "margem_alvo": resultado[3],
            "data_criacao": resultado[4],
            "ativo": resultado[5]
        }
    return None


def obter_categoria_por_nome(nome: str) -> dict:
    """
    Obtém uma categoria pelo nome.
    
    Args:
        nome (str): Nome da categoria
    
    Returns:
        dict: Dados da categoria ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, descricao, margem_alvo, data_criacao, ativo FROM categorias WHERE nome = ?",
        (nome.strip(),)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return {
            "id": resultado[0],
            "nome": resultado[1],
            "descricao": resultado[2],
            "margem_alvo": resultado[3],
            "data_criacao": resultado[4],
            "ativo": resultado[5]
        }
    return None


def obter_margem_categoria_por_nome(nome: str):
    """Obtém margem alvo de uma categoria pelo nome"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT margem_alvo FROM categorias WHERE nome = ?",
        (nome.strip(),)
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    return None


def atualizar_categoria(categoria_id: int, nome: str = None, descricao: str = None, margem_alvo: float = None) -> bool:
    """
    Atualiza dados de uma categoria.
    
    Args:
        categoria_id (int): ID da categoria
        nome (str, optional): Novo nome
        descricao (str, optional): Nova descrição
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if not any([nome, descricao is not None, margem_alvo is not None]):
        conn.close()
        return False
    
    updates = []
    params = []
    
    if nome:
        updates.append("nome = ?")
        params.append(nome.strip())
    
    if descricao is not None:
        updates.append("descricao = ?")
        params.append(descricao.strip() if descricao else None)

    if margem_alvo is not None:
        updates.append("margem_alvo = ?")
        params.append(margem_alvo)
    
    params.append(categoria_id)
    
    try:
        query = f"UPDATE categorias SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        sucesso = cursor.rowcount > 0
        conn.close()
        return sucesso
    except Exception as e:
        conn.close()
        raise ValueError(f"Erro ao atualizar categoria: {str(e)}")


def desativar_categoria(categoria_id: int) -> bool:
    """
    Desativa uma categoria (marca como inativa).
    
    Args:
        categoria_id (int): ID da categoria
    
    Returns:
        bool: True se desativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE categorias SET ativo = 0 WHERE id = ?",
        (categoria_id,)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def ativar_categoria(categoria_id: int) -> bool:
    """
    Ativa uma categoria (marca como ativa).
    
    Args:
        categoria_id (int): ID da categoria
    
    Returns:
        bool: True se ativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE categorias SET ativo = 1 WHERE id = ?",
        (categoria_id,)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def deletar_categoria(categoria_id: int) -> bool:
    """
    Deleta uma categoria.
    
    Args:
        categoria_id (int): ID da categoria
    
    Returns:
        bool: True se deletado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM categorias WHERE id = ?",
        (categoria_id,)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def contar_produtos_por_categoria(categoria_id: int) -> int:
    """
    Conta quantos produtos usam uma categoria.
    
    Args:
        categoria_id (int): ID da categoria
    
    Returns:
        int: Número de produtos na categoria
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Primeiro, obter o nome da categoria
    categoria = obter_categoria_por_id(categoria_id)
    if not categoria:
        conn.close()
        return 0
    
    cursor.execute(
        "SELECT COUNT(*) FROM produtos WHERE categoria = ? AND ativo = 1",
        (categoria["nome"],)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado[0] if resultado else 0
