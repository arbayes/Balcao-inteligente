"""
REPOSITÓRIO DE FORNECEDORES
Gerencia a persistência de fornecedores no banco de dados
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from app.database.connection import get_connection
from app.models.fornecedor import Fornecedor


def criar_tabela_fornecedores():
    """Cria a tabela de fornecedores se não existir"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                produtos_fornecidos TEXT,
                prazo_entrega INTEGER,
                dias_entrega TEXT,
                forma_pagamento TEXT,
                observacoes TEXT,
                ativo INTEGER DEFAULT 1,
                data_cadastro TEXT,
                ultima_compra TEXT
            )
        """)
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela fornecedores: {e}")
        raise
    finally:
        if conn:
            conn.close()


def inserir_fornecedor(fornecedor: Fornecedor) -> int:
    """
    Insere um novo fornecedor no banco de dados.
    
    Args:
        fornecedor (Fornecedor): Objeto fornecedor a ser inserido
    
    Returns:
        int: ID do fornecedor inserido
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO fornecedores (
                nome, cnpj, telefone, email, endereco, cidade, estado,
                produtos_fornecidos, prazo_entrega, dias_entrega, forma_pagamento,
                observacoes, ativo, data_cadastro, ultima_compra
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fornecedor.nome,
            fornecedor.cnpj,
            fornecedor.telefone,
            fornecedor.email,
            fornecedor.endereco,
            fornecedor.cidade,
            fornecedor.estado,
            fornecedor.produtos_fornecidos,
            fornecedor.prazo_entrega,
            fornecedor.dias_entrega,
            fornecedor.forma_pagamento,
            fornecedor.observacoes,
            1 if fornecedor.ativo else 0,
            fornecedor.data_cadastro.isoformat() if fornecedor.data_cadastro else datetime.now().isoformat(),
            fornecedor.ultima_compra.isoformat() if fornecedor.ultima_compra else None
        ))
        
        fornecedor_id = cursor.lastrowid
        conn.commit()
        return fornecedor_id
    except Exception as e:
        print(f"Erro ao inserir fornecedor: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def listar_fornecedores(ativo: Optional[bool] = None) -> List[Fornecedor]:
    """
    Lista todos os fornecedores.
    
    Args:
        ativo (Optional[bool]): Se especificado, filtra por status ativo
    
    Returns:
        List[Fornecedor]: Lista de fornecedores
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if ativo is None:
        cursor.execute("SELECT * FROM fornecedores ORDER BY nome")
    else:
        cursor.execute(
            "SELECT * FROM fornecedores WHERE ativo = ? ORDER BY nome",
            (1 if ativo else 0,)
        )
    
    rows = cursor.fetchall()
    conn.close()
    
    fornecedores = []
    for row in rows:
        fornecedor = Fornecedor(
            id=row[0],
            nome=row[1],
            cnpj=row[2],
            telefone=row[3],
            email=row[4],
            endereco=row[5],
            cidade=row[6],
            estado=row[7],
            produtos_fornecidos=row[8],
            prazo_entrega=row[9],
            dias_entrega=row[10],
            forma_pagamento=row[11],
            observacoes=row[12],
            ativo=bool(row[13]),
            data_cadastro=datetime.fromisoformat(row[14]) if row[14] else None,
            ultima_compra=datetime.fromisoformat(row[15]) if row[15] else None
        )
        fornecedores.append(fornecedor)
    
    return fornecedores


def obter_fornecedor_por_id(fornecedor_id: int) -> Optional[Fornecedor]:
    """
    Obtém um fornecedor pelo ID.
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        Optional[Fornecedor]: Fornecedor encontrado ou None
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,))
        row = cursor.fetchone()
        
        if row:
            return Fornecedor(
                id=row[0],
                nome=row[1],
                cnpj=row[2],
                telefone=row[3],
                email=row[4],
                endereco=row[5],
                cidade=row[6],
                estado=row[7],
                produtos_fornecidos=row[8],
                prazo_entrega=row[9],
                dias_entrega=row[10],
                forma_pagamento=row[11],
                observacoes=row[12],
                ativo=bool(row[13]),
                data_cadastro=datetime.fromisoformat(row[14]) if row[14] else None,
                ultima_compra=datetime.fromisoformat(row[15]) if row[15] else None
            )
        
        return None
    except Exception as e:
        print(f"Erro ao obter fornecedor por ID: {e}")
        return None
    finally:
        if conn:
            conn.close()


def atualizar_fornecedor(fornecedor: Fornecedor) -> bool:
    """
    Atualiza um fornecedor existente.
    
    Args:
        fornecedor (Fornecedor): Fornecedor com dados atualizados
    
    Returns:
        bool: True se atualizado com sucesso
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fornecedores SET
                nome = ?, cnpj = ?, telefone = ?, email = ?,
                endereco = ?, cidade = ?, estado = ?,
                produtos_fornecidos = ?, prazo_entrega = ?,
                dias_entrega = ?, forma_pagamento = ?, observacoes = ?, ativo = ?,
                ultima_compra = ?
            WHERE id = ?
        """, (
            fornecedor.nome,
            fornecedor.cnpj,
            fornecedor.telefone,
            fornecedor.email,
            fornecedor.endereco,
            fornecedor.cidade,
            fornecedor.estado,
            fornecedor.produtos_fornecidos,
            fornecedor.prazo_entrega,
            fornecedor.dias_entrega,
            fornecedor.forma_pagamento,
            fornecedor.observacoes,
            1 if fornecedor.ativo else 0,
            fornecedor.ultima_compra.isoformat() if fornecedor.ultima_compra else None,
            fornecedor.id
        ))
        
        sucesso = cursor.rowcount > 0
        conn.commit()
        return sucesso
    except Exception as e:
        print(f"Erro ao atualizar fornecedor: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def deletar_fornecedor(fornecedor_id: int) -> bool:
    """
    Deleta um fornecedor (desativa).
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        bool: True se deletado com sucesso
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE fornecedores SET ativo = 0 WHERE id = ?", (fornecedor_id,))
        
        sucesso = cursor.rowcount > 0
        conn.commit()
        return sucesso
    except Exception as e:
        print(f"Erro ao deletar fornecedor: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def ativar_fornecedor(fornecedor_id: int) -> bool:
    """
    Ativa um fornecedor.
    
    Args:
        fornecedor_id (int): ID do fornecedor
    
    Returns:
        bool: True se ativado com sucesso
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE fornecedores SET ativo = 1 WHERE id = ?", (fornecedor_id,))
    
    sucesso = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return sucesso


def buscar_fornecedores(termo: str) -> List[Fornecedor]:
    """
    Busca fornecedores por nome, CNPJ ou produtos.
    
    Args:
        termo (str): Termo de busca
    
    Returns:
        List[Fornecedor]: Lista de fornecedores encontrados
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    termo_like = f"%{termo}%"
    cursor.execute("""
        SELECT * FROM fornecedores 
        WHERE nome LIKE ? OR cnpj LIKE ? OR produtos_fornecidos LIKE ?
        ORDER BY nome
    """, (termo_like, termo_like, termo_like))
    
    rows = cursor.fetchall()
    conn.close()
    
    fornecedores = []
    for row in rows:
        fornecedor = Fornecedor(
            id=row[0],
            nome=row[1],
            cnpj=row[2],
            telefone=row[3],
            email=row[4],
            endereco=row[5],
            cidade=row[6],
            estado=row[7],
            produtos_fornecidos=row[8],
            prazo_entrega=row[9],
            dias_entrega=row[10],
            forma_pagamento=row[11],
            observacoes=row[12],
            ativo=bool(row[13]),
            data_cadastro=datetime.fromisoformat(row[14]) if row[14] else None,
            ultima_compra=datetime.fromisoformat(row[15]) if row[15] else None
        )
        fornecedores.append(fornecedor)
    
    return fornecedores


def obter_fornecedores_do_dia(dia_semana: int) -> List[Fornecedor]:
    """
    Obtém fornecedores que têm entrega no dia da semana especificado.
    
    Args:
        dia_semana (int): Dia da semana (0=Segunda, 1=Terça, ..., 6=Domingo)
    
    Returns:
        List[Fornecedor]: Lista de fornecedores com entrega no dia
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM fornecedores 
        WHERE ativo = 1 AND dias_entrega IS NOT NULL AND dias_entrega != ''
        ORDER BY nome
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    fornecedores_do_dia = []
    dia_str = str(dia_semana)
    
    for row in rows:
        dias_entrega = row[10]  # coluna dias_entrega
        if dias_entrega and dia_str in dias_entrega.split(','):
            fornecedor = Fornecedor(
                id=row[0],
                nome=row[1],
                cnpj=row[2],
                telefone=row[3],
                email=row[4],
                endereco=row[5],
                cidade=row[6],
                estado=row[7],
                produtos_fornecidos=row[8],
                prazo_entrega=row[9],
                dias_entrega=row[10],
                forma_pagamento=row[11],
                observacoes=row[12],
                ativo=bool(row[13]),
                data_cadastro=datetime.fromisoformat(row[14]) if row[14] else None,
                ultima_compra=datetime.fromisoformat(row[15]) if row[15] else None
            )
            fornecedores_do_dia.append(fornecedor)
    
    return fornecedores_do_dia
