from app.database.connection import get_connection
from app.models.produto import Produto


def criar_tabela_estoque():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                descricao TEXT,
                preco_compra REAL NOT NULL,
                preco_venda REAL NOT NULL,
                quantidade INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1,
                categoria TEXT DEFAULT 'Geral',
                margem_alvo REAL
            )
        """)
        cursor.execute("PRAGMA table_info(produtos)")
        colunas = [row[1] for row in cursor.fetchall()]
        if "margem_alvo" not in colunas:
            cursor.execute("ALTER TABLE produtos ADD COLUMN margem_alvo REAL")
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela produtos: {e}")
        raise
    finally:
        if conn:
            conn.close()


def inserir_produto(produto: Produto):
    """
    Insere um novo produto no estoque.
    
    Args:
        produto (Produto): Objeto produto com dados
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO produtos (nome, sku, descricao, preco_compra, preco_venda, quantidade, ativo, categoria, margem_alvo) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (produto.nome, produto.sku, produto.descricao, produto.preco_compra, produto.preco_venda, produto.quantidade, 1 if produto.ativo else 0, produto.categoria, produto.margem_alvo))
        conn.commit()
        produto_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e
    finally:
        conn.close()
    
    return produto_id


def obter_produto_por_sku(sku: str):
    """
    Obtém um produto pelo SKU (apenas se ativo).
    
    Args:
        sku (str): SKU do produto
    
    Returns:
        Produto: Objeto produto ou None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, sku, descricao, preco_compra, preco_venda, quantidade, ativo, categoria, margem_alvo FROM produtos WHERE sku = ? AND ativo = 1",
        (sku,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return Produto(
            id=resultado[0],
            nome=resultado[1],
            sku=resultado[2],
            descricao=resultado[3],
            preco_compra=resultado[4],
            preco_venda=resultado[5],
            quantidade=resultado[6],
            ativo=bool(resultado[7]),
            categoria=resultado[8],
            margem_alvo=resultado[9]
        )
    return None


def obter_produto_por_sku_inativo(sku: str):
    """
    Obtém um produto pelo SKU, mesmo se inativo.
    
    Args:
        sku (str): SKU do produto
    
    Returns:
        Produto: Objeto produto ou None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, sku, descricao, preco_compra, preco_venda, quantidade, ativo, categoria, margem_alvo FROM produtos WHERE sku = ?",
        (sku,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return Produto(
            id=resultado[0],
            nome=resultado[1],
            sku=resultado[2],
            descricao=resultado[3],
            preco_compra=resultado[4],
            preco_venda=resultado[5],
            quantidade=resultado[6],
            ativo=bool(resultado[7]),
            categoria=resultado[8],
            margem_alvo=resultado[9]
        )
    return None


def listar_produtos(busca: str = None, filtro_por: str = None):
    """
    Lista produtos ativos com busca avançada por múltiplos parâmetros.
    
    Args:
        busca (str, optional): Termo de busca
        filtro_por (str, optional): Campo para filtrar (nome, sku, descricao) - busca em todos se não especificado
    
    Returns:
        list[Produto]: Lista de produtos ativos que correspondem aos critérios
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Query base sempre filtra produtos ativos
    query = "SELECT id, nome, sku, descricao, preco_compra, preco_venda, quantidade, ativo, categoria, margem_alvo FROM produtos WHERE ativo = 1"
    params = []
    
    if busca:
        busca_formatado = f"%{busca}%"
        
        if filtro_por and filtro_por.lower() in ['nome', 'sku', 'descricao']:
            # Busca específica em um campo
            query += f" AND {filtro_por} LIKE ?"
            params.append(busca_formatado)
        else:
            # Busca em todos os campos (padrão)
            query += " AND (nome LIKE ? OR sku LIKE ? OR descricao LIKE ?)"
            params = [busca_formatado, busca_formatado, busca_formatado]
    
    query += " ORDER BY categoria ASC, nome ASC"
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()
    
    # Converter resultados em objetos Produto
    produtos = [
        Produto(
            id=resultado[0],
            nome=resultado[1],
            sku=resultado[2],
            descricao=resultado[3],
            preco_compra=resultado[4],
            preco_venda=resultado[5],
            quantidade=resultado[6],
            ativo=bool(resultado[7]),
            categoria=resultado[8],
            margem_alvo=resultado[9]
        )
        for resultado in resultados
    ]
    
    return produtos


def obter_produto_por_id(produto_id: int):
    """
    Obtém um produto específico pelo ID (apenas se ativo).
    
    Args:
        produto_id (int): ID do produto
    
    Returns:
        Produto: Objeto produto ou None
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, nome, sku, descricao, preco_compra, preco_venda, quantidade, ativo, categoria, margem_alvo FROM produtos WHERE id = ? AND ativo = 1",
        (produto_id,)
    )
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return Produto(
            id=resultado[0],
            nome=resultado[1],
            sku=resultado[2],
            descricao=resultado[3],
            preco_compra=resultado[4],
            preco_venda=resultado[5],
            quantidade=resultado[6],
            ativo=bool(resultado[7]),
            categoria=resultado[8],
            margem_alvo=resultado[9]
        )
    return None


def atualizar_produto(produto_id: int, nome: str = None, sku: str = None, descricao: str = None, preco_compra: float = None, preco_venda: float = None, quantidade: int = None, categoria: str = None, margem_alvo: float = None):
    """
    Atualiza dados do produto.
    
    Args:
        produto_id (int): ID do produto
        nome (str, optional): Novo nome
        sku (str, optional): Novo SKU
        descricao (str, optional): Nova descrição
        preco_compra (float, optional): Novo preço de compra
        preco_venda (float, optional): Novo preço de venda
        quantidade (int, optional): Nova quantidade
        categoria (str, optional): Nova categoria
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Validar que pelo menos um campo será atualizado
    if not any([nome, sku, descricao, preco_compra is not None, preco_venda is not None, quantidade is not None, categoria, margem_alvo is not None]):
        conn.close()
        return False
    
    # Construir query dinamicamente
    updates = []
    params = []
    
    if nome is not None:
        updates.append("nome = ?")
        params.append(nome)
    
    if sku is not None:
        updates.append("sku = ?")
        params.append(sku)
    
    if descricao is not None:
        updates.append("descricao = ?")
        params.append(descricao)
    
    if preco_compra is not None:
        updates.append("preco_compra = ?")
        params.append(preco_compra)
    
    if preco_venda is not None:
        updates.append("preco_venda = ?")
        params.append(preco_venda)
    
    if quantidade is not None:
        updates.append("quantidade = ?")
        params.append(quantidade)
    
    if categoria is not None:
        updates.append("categoria = ?")
        params.append(categoria)

    if margem_alvo is not None:
        updates.append("margem_alvo = ?")
        params.append(margem_alvo)
    
    params.append(produto_id)
    
    query = f"UPDATE produtos SET {', '.join(updates)} WHERE id = ? AND ativo = 1"
    
    cursor.execute(query, params)
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def aumentar_quantidade(produto_id: int, quantidade: int):
    """
    Aumenta a quantidade de um produto (entrada de estoque).
    
    Args:
        produto_id (int): ID do produto
        quantidade (int): Quantidade a adicionar
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE produtos SET quantidade = quantidade + ? WHERE id = ? AND ativo = 1",
        (quantidade, produto_id)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def diminuir_quantidade(produto_id: int, quantidade: int):
    """
    Diminui a quantidade de um produto (saída de estoque).
    
    Args:
        produto_id (int): ID do produto
        quantidade (int): Quantidade a remover
    
    Returns:
        bool: True se atualizado com sucesso e quantidade não ficou negativa
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se tem quantidade suficiente
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ? AND ativo = 1", (produto_id,))
    resultado = cursor.fetchone()
    
    if not resultado or resultado[0] < quantidade:
        conn.close()
        return False
    
    cursor.execute(
        "UPDATE produtos SET quantidade = quantidade - ? WHERE id = ? AND ativo = 1",
        (quantidade, produto_id)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def desativar_produto(produto_id: int):
    """
    Desativa um produto (soft delete).
    
    Args:
        produto_id (int): ID do produto a desativar
    
    Returns:
        bool: True se desativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ? AND ativo = 1", (produto_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso


def reativar_produto(produto_id: int):
    """
    Reativa um produto que foi desativado.
    
    Args:
        produto_id (int): ID do produto a reativar
    
    Returns:
        bool: True se reativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE produtos SET ativo = 1 WHERE id = ? AND ativo = 0", (produto_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso

def atualizar_categoria_produtos(categoria_antiga: str, categoria_nova: str) -> bool:
    """
    Atualiza a categoria de vários produtos de uma vez.
    
    Args:
        categoria_antiga (str): Categoria anterior
        categoria_nova (str): Nova categoria
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE produtos SET categoria = ? WHERE categoria = ?",
        (categoria_nova, categoria_antiga)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    conn.close()
    
    return sucesso
