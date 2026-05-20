"""
Serviço de Filtros Avançados - para buscas com período, faixa de valor, status
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

class FilterOperator(Enum):
    """Operadores de filtro"""
    IGUAL = "=="
    MAIOR = ">"
    MENOR = "<"
    MAIOR_IGUAL = ">="
    MENOR_IGUAL = "<="
    CONTEM = "contains"
    NAO_CONTEM = "not_contains"
    ENTRE = "between"

class AdvancedFilter:
    """Classe para filtros avançados"""
    
    def __init__(self):
        self.filters = {}
    
    def adicionar_filtro_periodo(self, campo: str, data_inicio: datetime, data_fim: datetime):
        """Adiciona filtro de período"""
        self.filters[f"{campo}_periodo"] = {
            'campo': campo,
            'operador': FilterOperator.ENTRE,
            'valor_min': data_inicio,
            'valor_max': data_fim
        }
    
    def adicionar_filtro_faixa_valor(self, campo: str, valor_min: float, valor_max: float):
        """Adiciona filtro de faixa de valor"""
        self.filters[f"{campo}_faixa"] = {
            'campo': campo,
            'operador': FilterOperator.ENTRE,
            'valor_min': valor_min,
            'valor_max': valor_max
        }
    
    def adicionar_filtro_status(self, campo: str, status: str):
        """Adiciona filtro de status"""
        self.filters[f"{campo}_status"] = {
            'campo': campo,
            'operador': FilterOperator.IGUAL,
            'valor': status
        }
    
    def adicionar_filtro_texto(self, campo: str, texto: str, parcial: bool = True):
        """Adiciona filtro de texto"""
        operador = FilterOperator.CONTEM if parcial else FilterOperator.IGUAL
        self.filters[f"{campo}_texto"] = {
            'campo': campo,
            'operador': operador,
            'valor': texto
        }
    
    def aplicar_filtros(self, dados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica todos os filtros aos dados"""
        resultado = dados
        
        for nome_filtro, config in self.filters.items():
            resultado = self._aplicar_filtro(resultado, config)
        
        return resultado
    
    def _aplicar_filtro(self, dados: List[Dict[str, Any]], config: Dict) -> List[Dict[str, Any]]:
        """Aplica um filtro específico"""
        campo = config['campo']
        operador = config['operador']
        
        resultado = []
        
        for item in dados:
            valor = item.get(campo)
            
            if valor is None:
                continue
            
            if operador == FilterOperator.IGUAL:
                if valor == config['valor']:
                    resultado.append(item)
            
            elif operador == FilterOperator.CONTEM:
                if isinstance(valor, str) and isinstance(config['valor'], str):
                    if config['valor'].lower() in valor.lower():
                        resultado.append(item)
            
            elif operador == FilterOperator.NAO_CONTEM:
                if isinstance(valor, str) and isinstance(config['valor'], str):
                    if config['valor'].lower() not in valor.lower():
                        resultado.append(item)
            
            elif operador == FilterOperator.MAIOR:
                if valor > config['valor']:
                    resultado.append(item)
            
            elif operador == FilterOperador.MENOR:
                if valor < config['valor']:
                    resultado.append(item)
            
            elif operador == FilterOperator.MAIOR_IGUAL:
                if valor >= config['valor']:
                    resultado.append(item)
            
            elif operador == FilterOperator.MENOR_IGUAL:
                if valor <= config['valor']:
                    resultado.append(item)
            
            elif operador == FilterOperator.ENTRE:
                if config['valor_min'] <= valor <= config['valor_max']:
                    resultado.append(item)
        
        return resultado
    
    def limpar_filtros(self):
        """Remove todos os filtros"""
        self.filters.clear()
    
    def obter_filtros_ativos(self) -> List[str]:
        """Retorna lista de filtros ativos"""
        return list(self.filters.keys())


class FilterService:
    """Serviço centralizado de filtros"""
    
    @staticmethod
    def filtrar_clientes(clientes: List[Dict], 
                        nome: Optional[str] = None,
                        cpf: Optional[str] = None,
                        data_cadastro_inicio: Optional[datetime] = None,
                        data_cadastro_fim: Optional[datetime] = None) -> List[Dict]:
        """Filtra lista de clientes"""
        resultado = clientes
        
        if nome:
            resultado = [c for c in resultado if nome.lower() in c.get('nome', '').lower()]
        
        if cpf:
            resultado = [c for c in resultado if cpf in c.get('cpf', '')]
        
        if data_cadastro_inicio and data_cadastro_fim:
            resultado = [c for c in resultado 
                        if FilterService._verificar_data(c.get('data_cadastro'), 
                                                        data_cadastro_inicio, 
                                                        data_cadastro_fim)]
        
        return resultado
    
    @staticmethod
    def filtrar_vendas(vendas: List[Dict],
                      data_inicio: Optional[datetime] = None,
                      data_fim: Optional[datetime] = None,
                      valor_min: Optional[float] = None,
                      valor_max: Optional[float] = None,
                      status: Optional[str] = None) -> List[Dict]:
        """Filtra lista de vendas"""
        resultado = vendas
        
        if data_inicio and data_fim:
            resultado = [v for v in resultado
                        if FilterService._verificar_data(v.get('data_venda'), 
                                                        data_inicio, 
                                                        data_fim)]
        
        if valor_min is not None:
            resultado = [v for v in resultado if v.get('valor_total', 0) >= valor_min]
        
        if valor_max is not None:
            resultado = [v for v in resultado if v.get('valor_total', 0) <= valor_max]
        
        if status:
            resultado = [v for v in resultado if v.get('status') == status]
        
        return resultado
    
    @staticmethod
    def filtrar_estoque(produtos: List[Dict],
                       categoria: Optional[str] = None,
                       quantidade_min: Optional[int] = None,
                       quantidade_max: Optional[int] = None,
                       preco_min: Optional[float] = None,
                       preco_max: Optional[float] = None) -> List[Dict]:
        """Filtra lista de estoque"""
        resultado = produtos
        
        if categoria:
            resultado = [p for p in resultado if p.get('categoria') == categoria]
        
        if quantidade_min is not None:
            resultado = [p for p in resultado if p.get('quantidade', 0) >= quantidade_min]
        
        if quantidade_max is not None:
            resultado = [p for p in resultado if p.get('quantidade', 0) <= quantidade_max]
        
        if preco_min is not None:
            resultado = [p for p in resultado if p.get('preco_venda', 0) >= preco_min]
        
        if preco_max is not None:
            resultado = [p for p in resultado if p.get('preco_venda', 0) <= preco_max]
        
        return resultado
    
    @staticmethod
    def _verificar_data(data_str: str, data_inicio: datetime, data_fim: datetime) -> bool:
        """Verifica se data está entre intervalo"""
        try:
            if isinstance(data_str, str):
                data = datetime.fromisoformat(data_str.split(' ')[0])
            else:
                data = data_str
            
            return data_inicio <= data <= data_fim
        except:
            return False
