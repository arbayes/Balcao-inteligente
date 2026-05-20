"""
Serviço de Backup Automático
Gerencia backups do banco de dados
"""

import shutil
from pathlib import Path
from datetime import datetime
import os


def fazer_backup() -> dict:
    """
    Faz backup do banco de dados.
    
    Returns:
        dict: Resultado da operação
    """
    try:
        # Caminhos
        db_path = Path("data/gerenciamento.db")
        backup_dir = Path("backups")
        
        # Criar diretório de backups se não existir
        backup_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = backup_dir / backup_filename
        
        # Verificar se o banco de dados existe
        if not db_path.exists():
            return {
                "sucesso": False,
                "mensagem": "Banco de dados não encontrado!"
            }
        
        # Copiar banco de dados
        shutil.copy2(db_path, backup_path)
        
        # Limpar backups antigos (manter apenas os 10 mais recentes)
        limpar_backups_antigos(backup_dir, manter=10)
        
        return {
            "sucesso": True,
            "mensagem": f"Backup criado com sucesso!\n{backup_filename}",
            "caminho": str(backup_path.absolute())
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao fazer backup: {str(e)}"
        }


def limpar_backups_antigos(backup_dir: Path, manter: int = 10):
    """
    Remove backups antigos, mantendo apenas os mais recentes.
    
    Args:
        backup_dir (Path): Diretório de backups
        manter (int): Quantidade de backups a manter
    """
    try:
        # Listar todos os arquivos de backup
        backups = list(backup_dir.glob("backup_*.db"))
        
        # Ordenar por data de modificação (mais recente primeiro)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Deletar backups excedentes
        for backup in backups[manter:]:
            backup.unlink()
            
    except Exception as e:
        print(f"Erro ao limpar backups antigos: {e}")


def listar_backups() -> list:
    """
    Lista todos os backups disponíveis.
    
    Returns:
        list: Lista de backups com informações
    """
    try:
        backup_dir = Path("backups")
        
        if not backup_dir.exists():
            return []
        
        backups = []
        for backup_file in backup_dir.glob("backup_*.db"):
            stat = backup_file.stat()
            backups.append({
                "nome": backup_file.name,
                "caminho": str(backup_file.absolute()),
                "tamanho": stat.st_size,
                "data": datetime.fromtimestamp(stat.st_mtime)
            })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['data'], reverse=True)
        
        return backups
        
    except Exception as e:
        print(f"Erro ao listar backups: {e}")
        return []


def restaurar_backup(backup_path: str) -> dict:
    """
    Restaura um backup do banco de dados.
    
    Args:
        backup_path (str): Caminho do arquivo de backup
    
    Returns:
        dict: Resultado da operação
    """
    try:
        db_path = Path("data/gerenciamento.db")
        backup_file = Path(backup_path)
        
        # Verificar se o backup existe
        if not backup_file.exists():
            return {
                "sucesso": False,
                "mensagem": "Arquivo de backup não encontrado!"
            }
        
        # Fazer backup do banco atual antes de restaurar
        if db_path.exists():
            backup_atual = db_path.parent / f"gerenciamento_antes_restauracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_path, backup_atual)
        
        # Restaurar backup
        shutil.copy2(backup_file, db_path)
        
        return {
            "sucesso": True,
            "mensagem": "Backup restaurado com sucesso!"
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao restaurar backup: {str(e)}"
        }


def obter_tamanho_formatado(bytes: int) -> str:
    """
    Formata tamanho de arquivo em bytes para formato legível.
    
    Args:
        bytes (int): Tamanho em bytes
    
    Returns:
        str: Tamanho formatado
    """
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unidade}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"
