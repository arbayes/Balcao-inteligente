"""
Serviço de Metas e KPIs - Dashboard com metas de vendas, ticket médio, etc
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class MetasService:
    """Gerencia metas e KPIs do negócio"""
    
    CONFIG_FILE = Path(__file__).parent.parent.parent / "metas_config.json"
    
    def __init__(self):
        self.metas = self._load_metas()
    
    def _load_metas(self) -> Dict:
        """Carrega configurações de metas"""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar metas: {e}")
        
        return self._metas_padrao()
    
    def _metas_padrao(self) -> Dict:
        """Retorna configuração padrão de metas"""
        return {
            'meta_vendas_mensal': 10000.0,
            'ticket_medio_alvo': 500.0,
            'margem_lucro_alvo': 0.30,  # 30%
            'meta_clientes_novos': 10,
            'meta_recebimentos': 9000.0,
            'meta_compras': 5000.0
        }
    
    def _save_metas(self):
        """Salva metas em arquivo"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.metas, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar metas: {e}")
    
    def set_meta(self, chave: str, valor: float):
        """Define uma meta específica"""
        self.metas[chave] = valor
        self._save_metas()
    
    def get_meta(self, chave: str) -> Optional[float]:
        """Obtém valor de uma meta"""
        return self.metas.get(chave)
    
    def calcular_kpis(self, vendas: List[Dict], clientes: List[Dict], compras: List[Dict]) -> Dict:
        """Calcula todos os KPIs"""
        kpis = {
            'vendas_totais': 0,
            'ticket_medio': 0,
            'quantidade_vendas': 0,
            'margem_lucro': 0,
            'clientes_novos': 0,
            'recebimentos': 0,
            'compras_totais': 0,
            'metas': self.metas,
            'progresso': {}
        }
        
        # Calcular vendas totais e ticket médio
        if vendas:
            vendas_mes = self._filtrar_mes_atual(vendas, 'data_venda')
            kpis['quantidade_vendas'] = len(vendas_mes)
            kpis['vendas_totais'] = sum(v.get('valor_total', 0) for v in vendas_mes)
            
            if kpis['quantidade_vendas'] > 0:
                kpis['ticket_medio'] = kpis['vendas_totais'] / kpis['quantidade_vendas']
        
        # Calcular clientes novos do mês
        if clientes:
            clientes_novos = self._filtrar_mes_atual(clientes, 'data_cadastro')
            kpis['clientes_novos'] = len(clientes_novos)
        
        # Calcular compras
        if compras:
            compras_mes = self._filtrar_mes_atual(compras, 'data_compra')
            kpis['compras_totais'] = sum(c.get('valor_total', 0) for c in compras_mes)
        
        # Calcular progresso em relação às metas
        kpis['progresso']['vendas'] = {
            'valor': kpis['vendas_totais'],
            'meta': self.metas.get('meta_vendas_mensal', 0),
            'percentual': (kpis['vendas_totais'] / self.metas.get('meta_vendas_mensal', 1)) * 100
        }
        
        kpis['progresso']['ticket_medio'] = {
            'valor': round(kpis['ticket_medio'], 2),
            'meta': self.metas.get('ticket_medio_alvo', 0),
            'percentual': (kpis['ticket_medio'] / self.metas.get('ticket_medio_alvo', 1)) * 100
        }
        
        kpis['progresso']['clientes'] = {
            'valor': kpis['clientes_novos'],
            'meta': self.metas.get('meta_clientes_novos', 0),
            'percentual': (kpis['clientes_novos'] / self.metas.get('meta_clientes_novos', 1)) * 100
        }
        
        kpis['progresso']['compras'] = {
            'valor': kpis['compras_totais'],
            'meta': self.metas.get('meta_compras', 0),
            'percentual': (kpis['compras_totais'] / self.metas.get('meta_compras', 1)) * 100
        }
        
        return kpis
    
    def _filtrar_mes_atual(self, items: List[Dict], campo_data: str) -> List[Dict]:
        """Filtra itens do mês atual"""
        hoje = datetime.now()
        inicio_mes = datetime(hoje.year, hoje.month, 1)
        
        resultado = []
        for item in items:
            data_str = item.get(campo_data)
            if data_str:
                try:
                    if isinstance(data_str, str):
                        data = datetime.fromisoformat(data_str.split(' ')[0])
                    else:
                        data = data_str
                    
                    if data >= inicio_mes:
                        resultado.append(item)
                except:
                    pass
        
        return resultado
    
    def gerar_relatorio_metas(self, kpis: Dict) -> Dict:
        """Gera relatório de metas com análise"""
        relatorio = {
            'data': datetime.now().isoformat(),
            'resumo': {},
            'avisos': []
        }
        
        # Análise de vendas
        vendas_prog = kpis['progresso'].get('vendas', {})
        percentual_vendas = vendas_prog.get('percentual', 0)
        
        relatorio['resumo']['vendas'] = {
            'valor': vendas_prog.get('valor', 0),
            'meta': vendas_prog.get('meta', 0),
            'percentual': round(percentual_vendas, 1),
            'status': self._classificar_progresso(percentual_vendas)
        }
        
        if percentual_vendas < 50:
            relatorio['avisos'].append("⚠️ Vendas muito abaixo da meta!")
        elif percentual_vendas > 100:
            relatorio['avisos'].append("✅ Meta de vendas atingida!")
        
        # Análise de ticket médio
        ticket_prog = kpis['progresso'].get('ticket_medio', {})
        percentual_ticket = ticket_prog.get('percentual', 0)
        
        relatorio['resumo']['ticket_medio'] = {
            'valor': round(ticket_prog.get('valor', 0), 2),
            'meta': ticket_prog.get('meta', 0),
            'percentual': round(percentual_ticket, 1),
            'status': self._classificar_progresso(percentual_ticket)
        }
        
        # Análise de clientes novos
        clientes_prog = kpis['progresso'].get('clientes', {})
        percentual_clientes = clientes_prog.get('percentual', 0)
        
        relatorio['resumo']['clientes_novos'] = {
            'valor': clientes_prog.get('valor', 0),
            'meta': clientes_prog.get('meta', 0),
            'percentual': round(percentual_clientes, 1),
            'status': self._classificar_progresso(percentual_clientes)
        }
        
        return relatorio
    
    def _classificar_progresso(self, percentual: float) -> str:
        """Classifica progresso em relação à meta"""
        if percentual >= 100:
            return 'META ATINGIDA'
        elif percentual >= 75:
            return 'BOM'
        elif percentual >= 50:
            return 'REGULAR'
        else:
            return 'CRÍTICO'


# Singleton global
_metas_service = None

def get_metas_service() -> MetasService:
    """Retorna instância global do serviço de metas"""
    global _metas_service
    if _metas_service is None:
        _metas_service = MetasService()
    return _metas_service
