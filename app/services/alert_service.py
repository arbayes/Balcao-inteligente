"""
Serviço de Alertas - Monitora estoque, clientes em atraso, etc
"""

from datetime import datetime, timedelta
from typing import List, Dict
from app.services.estoque_service import listar_produtos
from app.services.clientes_service import buscar_clientes
from app.services.vendas_fiadas_service import obter_divida_cliente

class Alert:
    """Modelo de alerta"""
    def __init__(self, tipo: str, titulo: str, mensagem: str, severidade: str = "info"):
        self.tipo = tipo  # estoque, cliente, compra
        self.titulo = titulo
        self.mensagem = mensagem
        self.severidade = severidade  # info, warning, error
        self.data = datetime.now()
        self.lido = False

class AlertService:
    """Gerenciador de alertas do sistema"""
    
    def __init__(self):
        self.alertas: List[Alert] = []
        self.config = {
            'estoque_minimo': 5,
            'dias_atraso_cliente': 30,
            'dias_atraso_compra': 7
        }
    
    def gerar_alertas(self) -> List[Alert]:
        """Gera todos os alertas do sistema"""
        self.alertas = []
        
        # Alertas de estoque
        self._alertas_estoque()
        
        # Alertas de clientes em atraso
        self._alertas_clientes_atraso()
        
        # Alertas de compras vencidas
        self._alertas_compras_vencidas()
        
        return self.alertas
    
    def _alertas_estoque(self):
        """Verifica produtos com estoque baixo"""
        try:
            produtos = listar_produtos()
            
            for produto in produtos:
                # Produto pode ser dict ou object
                if isinstance(produto, dict):
                    quantidade = produto.get('quantidade', 0)
                    nome = produto.get('nome', 'Produto desconhecido')
                else:
                    quantidade = getattr(produto, 'quantidade', 0)
                    nome = getattr(produto, 'nome', 'Produto desconhecido')
                
                if quantidade < self.config['estoque_minimo']:
                    alerta = Alert(
                        tipo='estoque',
                        titulo=f'📦 Estoque Baixo',
                        mensagem=f'{nome} - Quantidade: {quantidade}',
                        severidade='warning' if quantidade > 0 else 'error'
                    )
                    self.alertas.append(alerta)
        
        except Exception as e:
            print(f"Erro ao gerar alertas de estoque: {e}")
    
    def _alertas_clientes_atraso(self):
        """Verifica clientes com atraso de pagamento"""
        try:
            clientes = buscar_clientes()
            dias_atraso = self.config['dias_atraso_cliente']
            
            for cliente in clientes:
                divida = obter_divida_cliente(cliente['id'])
                
                if divida['inadimplente']:
                    alerta = Alert(
                        tipo='cliente',
                        titulo='⚠️ Cliente Inadimplente',
                        mensagem=f"{cliente['nome']} - Débito: R$ {divida['divida_total']:.2f}",
                        severidade='error'
                    )
                    self.alertas.append(alerta)
                
                elif divida['divida_total'] > 0:
                    # Verificar dias de atraso
                    alerta = Alert(
                        tipo='cliente',
                        titulo='⏳ Cliente com Débito',
                        mensagem=f"{cliente['nome']} - Débito: R$ {divida['divida_total']:.2f}",
                        severidade='warning'
                    )
                    self.alertas.append(alerta)
        
        except Exception as e:
            print(f"Erro ao gerar alertas de clientes: {e}")
    
    def _alertas_compras_vencidas(self):
        """Verifica compras não entregues"""
        try:
            from app.database.compras_repository import ComprasRepository
            repo = ComprasRepository()
            
            # Tentar obter compras
            try:
                compras = repo.listar_compras()
            except:
                # Se não conseguir listar, compras não estão configuradas ainda
                return
            
            dias_atraso = self.config['dias_atraso_compra']
            
            for compra in compras:
                if compra.status == "PENDING":
                    data_vencimento = compra.data_entrega_esperada
                    dias_passados = (datetime.now() - data_vencimento).days
                    
                    if dias_passados > dias_atraso:
                        alerta = Alert(
                            tipo='compra',
                            titulo='📦 Compra Vencida',
                            mensagem=f'Compra #{compra.id} - {dias_passados} dias de atraso',
                            severidade='error'
                        )
                        self.alertas.append(alerta)
        
        except ImportError:
            # Módulo de compras não disponível ainda
            pass
        except Exception as e:
            print(f"Erro ao gerar alertas de compras: {e}")
    
    def obter_alertas_nao_lidos(self) -> List[Alert]:
        """Retorna alertas não lidos"""
        return [a for a in self.alertas if not a.lido]
    
    def marcar_como_lido(self, indice: int):
        """Marca alerta como lido"""
        if 0 <= indice < len(self.alertas):
            self.alertas[indice].lido = True
    
    def obter_contador_alertas(self) -> Dict[str, int]:
        """Retorna contagem por severidade"""
        return {
            'error': len([a for a in self.alertas if a.severidade == 'error']),
            'warning': len([a for a in self.alertas if a.severidade == 'warning']),
            'info': len([a for a in self.alertas if a.severidade == 'info']),
            'total': len(self.alertas)
        }
    
    def configurar_limites(self, estoque_minimo: int = None, dias_atraso_cliente: int = None, dias_atraso_compra: int = None):
        """Atualiza limites de alertas"""
        if estoque_minimo is not None:
            self.config['estoque_minimo'] = estoque_minimo
        if dias_atraso_cliente is not None:
            self.config['dias_atraso_cliente'] = dias_atraso_cliente
        if dias_atraso_compra is not None:
            self.config['dias_atraso_compra'] = dias_atraso_compra


# Singleton global
_alert_service = None

def get_alert_service() -> AlertService:
    """Retorna instância global do serviço de alertas"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
