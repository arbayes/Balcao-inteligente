"""
Sistema de Backup Automático - APScheduler
Requer: pip install apscheduler
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

class BackupScheduler:
    """Gerencia backups automáticos"""
    
    def __init__(self, db_path: str, backup_dir: str = "backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.config_file = self.backup_dir / "backup_config.json"
        self.config = self._load_config()
        self.scheduler = None
        self.callback = None
    
    def _load_config(self) -> dict:
        """Carrega configurações de backup"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config de backup: {e}")
        
        return {
            'enabled': True,
            'frequency': 'daily',  # daily, weekly, monthly
            'time': '02:00',
            'retention_days': 30,
            'last_backup': None
        }
    
    def _save_config(self):
        """Salva configurações"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar config de backup: {e}")
    
    def fazer_backup(self) -> bool:
        """Executa backup manual do banco"""
        try:
            if not self.db_path.exists():
                print(f"Banco de dados não encontrado: {self.db_path}")
                return False
            
            # Criar nome com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            # Copiar arquivo
            shutil.copy2(self.db_path, backup_path)
            
            # Atualizar config
            self.config['last_backup'] = datetime.now().isoformat()
            self._save_config()
            
            # Limpar backups antigos
            self._limpar_backups_antigos()
            
            # Chamar callback se configurado
            if self.callback:
                self.callback(f"✅ Backup realizado: {backup_name}")
            
            print(f"Backup criado: {backup_path}")
            return True
        
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")
            if self.callback:
                self.callback(f"❌ Erro no backup: {str(e)}")
            return False
    
    def _limpar_backups_antigos(self):
        """Remove backups mais antigos que o período de retenção"""
        try:
            dias_retencao = self.config.get('retention_days', 30)
            data_limite = datetime.now().timestamp() - (dias_retencao * 86400)
            
            for arquivo in self.backup_dir.glob("backup_*.db"):
                if arquivo.stat().st_mtime < data_limite:
                    arquivo.unlink()
                    print(f"Backup antigo removido: {arquivo.name}")
        
        except Exception as e:
            print(f"Erro ao limpar backups: {e}")
    
    def restaurar_backup(self, backup_nome: str) -> bool:
        """Restaura a partir de um backup"""
        try:
            backup_path = self.backup_dir / backup_nome
            
            if not backup_path.exists():
                print(f"Backup não encontrado: {backup_path}")
                return False
            
            # Criar backup da versão atual (segurança)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_atual = self.backup_dir / f"backup_anterior_{timestamp}.db"
            shutil.copy2(self.db_path, backup_atual)
            
            # Restaurar
            shutil.copy2(backup_path, self.db_path)
            
            if self.callback:
                self.callback(f"✅ Backup restaurado: {backup_nome}")
            
            print(f"Backup restaurado: {backup_nome}")
            return True
        
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            if self.callback:
                self.callback(f"❌ Erro ao restaurar: {str(e)}")
            return False
    
    def listar_backups(self) -> list:
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            for arquivo in sorted(self.backup_dir.glob("backup_*.db"), reverse=True):
                stat = arquivo.stat()
                backups.append({
                    'nome': arquivo.name,
                    'tamanho': f"{stat.st_size / 1024:.1f} KB",
                    'data': datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
                    'path': str(arquivo)
                })
            return backups
        except Exception as e:
            print(f"Erro ao listar backups: {e}")
            return []
    
    def configurar(self, enabled: bool = None, frequency: str = None, time: str = None, retention_days: int = None):
        """Configura opções de backup"""
        if enabled is not None:
            self.config['enabled'] = enabled
        if frequency is not None:
            self.config['frequency'] = frequency
        if time is not None:
            self.config['time'] = time
        if retention_days is not None:
            self.config['retention_days'] = retention_days
        
        self._save_config()
    
    def set_callback(self, callback: Callable):
        """Define callback para notificações"""
        self.callback = callback
    
    def iniciar_scheduler_apscheduler(self):
        """Inicia scheduler automático com APScheduler"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            
            self.scheduler = BackgroundScheduler()
            
            if self.config['enabled']:
                # Agendar backup
                hora, minuto = map(int, self.config['time'].split(':'))
                
                if self.config['frequency'] == 'daily':
                    trigger = CronTrigger(hour=hora, minute=minuto)
                elif self.config['frequency'] == 'weekly':
                    trigger = CronTrigger(day_of_week='mon', hour=hora, minute=minuto)
                else:  # monthly
                    trigger = CronTrigger(day=1, hour=hora, minute=minuto)
                
                self.scheduler.add_job(
                    self.fazer_backup,
                    trigger=trigger,
                    id='backup_job',
                    name='Backup Automático',
                    replace_existing=True
                )
                
                self.scheduler.start()
                print("Scheduler de backup iniciado")
        
        except ImportError:
            print("APScheduler não está instalado. Execute: pip install apscheduler")
        except Exception as e:
            print(f"Erro ao iniciar scheduler: {e}")
    
    def parar_scheduler(self):
        """Para o scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler parado")


# Singleton global
_backup_scheduler = None

def get_backup_scheduler(db_path: str = None) -> BackupScheduler:
    """Retorna instância global do scheduler de backup"""
    global _backup_scheduler
    
    if _backup_scheduler is None:
        if db_path is None:
            from app.config.settings import DB_PATH
            db_path = str(DB_PATH)
        
        _backup_scheduler = BackupScheduler(db_path)
    
    return _backup_scheduler
