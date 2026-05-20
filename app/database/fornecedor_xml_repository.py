"""
REPOSITÓRIO DE IMPORTAÇÕES XML POR FORNECEDOR
Armazena histórico de XML importados por fornecedor
"""

from datetime import datetime
from typing import List, Dict

from app.database.connection import get_connection


def criar_tabela_fornecedor_xml_imports():
    """Cria a tabela de importações XML por fornecedor"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fornecedor_xml_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fornecedor_id INTEGER NOT NULL,
                caminho_arquivo TEXT,
                nome_arquivo TEXT,
                data_importacao TEXT,
                total_itens INTEGER DEFAULT 0,
                produtos_criados INTEGER DEFAULT 0,
                produtos_atualizados INTEGER DEFAULT 0,
                avisos TEXT,
                comparacoes_preco TEXT,
                FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
            )
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela fornecedor_xml_imports: {e}")
        raise
    finally:
        if conn:
            conn.close()


def registrar_importacao_fornecedor(
    fornecedor_id: int,
    caminho_arquivo: str,
    nome_arquivo: str,
    total_itens: int,
    produtos_criados: int,
    produtos_atualizados: int,
    avisos: str,
    comparacoes_preco: str,
    data_importacao: str | None = None
) -> int:
    """Registra uma importação XML para um fornecedor"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fornecedor_xml_imports (
                fornecedor_id, caminho_arquivo, nome_arquivo, data_importacao,
                total_itens, produtos_criados, produtos_atualizados, avisos, comparacoes_preco
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fornecedor_id,
                caminho_arquivo,
                nome_arquivo,
                data_importacao or datetime.now().isoformat(),
                total_itens,
                produtos_criados,
                produtos_atualizados,
                avisos,
                comparacoes_preco,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao registrar importação XML: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def listar_importacoes_fornecedor(fornecedor_id: int) -> List[Dict]:
    """Lista importações XML de um fornecedor"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, fornecedor_id, caminho_arquivo, nome_arquivo, data_importacao,
               total_itens, produtos_criados, produtos_atualizados, avisos, comparacoes_preco
        FROM fornecedor_xml_imports
        WHERE fornecedor_id = ?
        ORDER BY data_importacao DESC
        """,
        (fornecedor_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    imports = []
    for row in rows:
        imports.append(
            {
                "id": row[0],
                "fornecedor_id": row[1],
                "caminho_arquivo": row[2],
                "nome_arquivo": row[3],
                "data_importacao": row[4],
                "total_itens": row[5],
                "produtos_criados": row[6],
                "produtos_atualizados": row[7],
                "avisos": row[8],
                "comparacoes_preco": row[9],
            }
        )

    return imports
