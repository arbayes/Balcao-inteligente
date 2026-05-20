from app.database.clientes_repository import (
    criar_tabela_clientes, 
    inserir_cliente, 
    listar_clientes,
    atualizar_cliente,
    desativar_cliente,
    reativar_cliente,
    obter_cliente_por_id,
    obter_clientes_vip,
    obter_clientes_inativos_desde_dias,
    atualizar_valor_gasto
)
from app.models.cliente import Cliente

def cadastrar_cliente(nome: str, cpf: str, telefone: str = None, email: str = None, endereco: str = None, vip: bool = False) -> dict:
    """
    Cadastra um novo cliente com todos os campos opcionais.
    
    Args:
        nome (str): Nome do cliente
        cpf (str): CPF do cliente (11 dígitos)
        telefone (str, optional): Telefone do cliente
        email (str, optional): Email do cliente
        endereco (str, optional): Endereço do cliente
        vip (bool, optional): Se o cliente é VIP
    
    Returns:
        dict: Resultado com sucesso e mensagem
    """
    if not nome or not nome.strip():
        return {
            "sucesso": False,
            "mensagem": "Nome não pode estar vazio."
        }
    
    if not cpf or not cpf.isdigit() or len(cpf) != 11:
        return {
            "sucesso": False,
            "mensagem": "CPF deve conter exatamente 11 dígitos."
        }
    
    try:
        cliente = Cliente(
            nome=nome.strip(), 
            cpf=cpf,
            telefone=telefone.strip() if telefone else None,
            email=email.strip() if email else None,
            endereco=endereco.strip() if endereco else None,
            vip=vip
        )
        inserir_cliente(cliente)
        
        return {
            "sucesso": True,
            "mensagem": f"Cliente '{nome}' cadastrado com sucesso."
        }
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cadastrar cliente: {str(e)}"
        }


def buscar_clientes(termo: str = None, campo: str = None) -> list:
    """
    Busca clientes ativos de forma moderna e flexível.
    
    Args:
        termo (str, optional): Termo para buscar (busca em todos os campos por padrão)
        campo (str, optional): Campo específico (nome, cpf, telefone, email)
    
    Returns:
        list: Lista de clientes com todos os campos
    
    Exemplos:
        buscar_clientes()  # Retorna todos os clientes ativos
        buscar_clientes("João")  # Busca por nome, cpf, telefone ou email
        buscar_clientes("12345678900", "cpf")  # Busca específica por CPF
    """
    clientes = listar_clientes(busca=termo, filtro_por=campo)
    
    return [
        {
            "id": c.id,
            "nome": c.nome,
            "cpf": c.cpf,
            "telefone": c.telefone,
            "email": c.email,
            "endereco": c.endereco,
            "vip": c.vip,
            "data_cadastro": c.data_cadastro,
            "data_ultima_compra": c.data_ultima_compra,
            "valor_total_gasto": c.valor_total_gasto,
            "ativo": c.ativo
        }
        for c in clientes
    ]


def obter_cliente(cliente_id: int) -> dict:
    """
    Obtém um cliente específico pelo ID.
    
    Args:
        cliente_id (int): ID do cliente
    
    Returns:
        dict: Dados do cliente com todos os campos ou None se não encontrado
    
    Exemplo:
        cliente = obter_cliente(1)
    """
    cliente = obter_cliente_por_id(cliente_id)
    
    if cliente:
        return {
            "id": cliente.id,
            "nome": cliente.nome,
            "cpf": cliente.cpf,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "endereco": cliente.endereco,
            "vip": cliente.vip,
            "data_cadastro": cliente.data_cadastro,
            "data_ultima_compra": cliente.data_ultima_compra,
            "valor_total_gasto": cliente.valor_total_gasto,
            "ativo": cliente.ativo
        }
    return None


def editar_cliente(cliente_id: int, **kwargs) -> dict:
    """
    Edita dados de um cliente existente.
    
    Args:
        cliente_id (int): ID do cliente
        **kwargs: Campos a atualizar (nome, cpf, telefone, email, endereco, vip)
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplos:
        editar_cliente(1, nome="João Silva")
        editar_cliente(1, telefone="31999999999", email="joao@email.com")
        editar_cliente(1, vip=True)
    """
    if not kwargs:
        return {
            "sucesso": False,
            "mensagem": "Nenhum campo para atualizar foi fornecido."
        }
    
    # Validações básicas
    if 'nome' in kwargs and kwargs['nome'] and not kwargs['nome'].strip():
        return {
            "sucesso": False,
            "mensagem": "Nome não pode estar vazio."
        }
    
    if 'cpf' in kwargs and kwargs['cpf'] and (not kwargs['cpf'].isdigit() or len(kwargs['cpf']) != 11):
        return {
            "sucesso": False,
            "mensagem": "CPF deve conter exatamente 11 dígitos."
        }
    
    sucesso = atualizar_cliente(cliente_id, **kwargs)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": "Cliente atualizado com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Cliente não encontrado ou não foi possível atualizar."
        }


def deletar_cliente(cliente_id: int) -> dict:
    """
    Deleta um cliente (soft delete - apenas desativa).
    
    Args:
        cliente_id (int): ID do cliente
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        deletar_cliente(1)
    """
    sucesso = desativar_cliente(cliente_id)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": "Cliente deletado com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Cliente não encontrado ou já foi deletado."
        }


def reativar_cliente_service(cliente_id: int) -> dict:
    """
    Reativa um cliente que foi deletado.
    
    Args:
        cliente_id (int): ID do cliente
    
    Returns:
        dict: Resultado da operação com sucesso e mensagem
    
    Exemplo:
        reativar_cliente_service(1)
    """
    sucesso = reativar_cliente(cliente_id)
    
    if sucesso:
        return {
            "sucesso": True,
            "mensagem": "Cliente reativado com sucesso."
        }
    else:
        return {
            "sucesso": False,
            "mensagem": "Cliente não encontrado ou já está ativo."
        }
