# Balcão Inteligente

Sistema desktop para controle de bar, mercearia e pequenos comércios.

**Versão atual:** 0.6 beta  
**Base do projeto:** Python + PyQt6 + SQLite  
**Status:** em desenvolvimento, mas já utilizável para testes reais de rotina.

## Sobre o Projeto

O Balcão Inteligente nasceu para organizar aquelas partes do comércio que costumam ficar espalhadas: estoque, clientes que compram fiado, fechamento de caixa, compras de fornecedores, relatórios e alertas.

A ideia não é substituir a correria do balcão, e sim oferecer um lugar confiável para registrar o que importa. Por isso, o app possui duas formas de venda: uma mais detalhada, com baixa automática de produtos no estoque, e uma venda rápida para quando só dá tempo de registrar o valor no caixa.

## O Que o Sistema Faz Hoje

### Dashboard

- Mostra indicadores gerais do negócio.
- Resume clientes, produtos, valor em estoque, estoque baixo e vendas fiadas.
- Ajuda a identificar rapidamente o que precisa de atenção.

### Clientes

- Cadastro, edição e desativação de clientes.
- Busca por nome, CPF, telefone ou e-mail.
- Marcação de cliente VIP.
- Histórico de valor gasto e última compra.

### Estoque

- Cadastro completo de produtos.
- Controle de quantidade, preço de compra, preço de venda e margem.
- Entrada e saída manual de estoque.
- Categorias de produtos com criação, edição e exclusão definitiva.
- Avisos para produtos com estoque baixo.

### PDV

- Venda por produto com baixa automática no estoque.
- Venda rápida por valor, pensada para a correria do atendimento.
- Registro no caixa com formas de pagamento como dinheiro, Pix, cartão ou outros.
- Histórico das vendas realizadas pelo PDV.
- O fiado fica fora do PDV de propósito, pois precisa estar vinculado a um cliente.

### Vendas Fiadas

- Lançamento de vendas fiadas por cliente.
- Baixa automática do estoque nos produtos vendidos.
- Controle de dívidas pendentes, pagas e inadimplentes.
- Detalhamento por cliente.
- Exclusão de venda com reposição de estoque quando a venda já havia baixado produtos.
- Ferramenta para corrigir estoque de vendas antigas registradas antes da integração com o estoque.

### Caixa

- Abertura de caixa com saldo inicial.
- Lançamento de entradas e saídas.
- Integração com vendas registradas pelo PDV.
- Fechamento com saldo esperado, saldo contado e diferença.
- Histórico para conferência do movimento.

### Fornecedores e Compras

- Cadastro e gerenciamento de fornecedores.
- Registro de compras por fornecedor.
- Marcação de compra como entregue, adicionando os itens ao estoque.
- Proteção contra duplicidade no lançamento de compras.
- Exclusão de compra entregue com ajuste reverso no estoque, quando possível.
- Importação de XML de NF-e para cadastrar ou atualizar produtos.
- Histórico de XMLs importados por fornecedor.

### Relatórios e Gráficos

- Painel visual com resumo do negócio.
- Abas para resumo, caixa, alertas, rankings e ações sugeridas.
- Gráficos focados em tomada de decisão, como dinheiro parado em estoque e relação entre caixa e fiado.
- Exportação de relatórios para PDF e Excel.

### Automações e Alertas

- Automações simples para acompanhar estoque baixo, fiado pendente e outras rotinas.
- Execução periódica dentro do app.
- Alertas na barra de status.
- Backup automático ao abrir, ao fechar e em intervalos durante o uso.

## Mudanças Mais Recentes da Versão 0.6 Beta

- Fechamento de caixa adicionado e integrado aos relatórios.
- Área de relatórios reformulada para ficar mais visual e menos textual.
- Gráficos reorganizados para mostrar informações relevantes para tomada de decisão.
- PDV criado com venda por produto e venda rápida.
- Vendas fiadas agora baixam estoque automaticamente.
- Compras entregues agora entram no estoque.
- Categorias podem ser excluídas definitivamente.
- Componentes visuais padronizados em botões, tabelas, cards e diálogos.
- Correções de contraste em telas de inadimplentes e detalhes de fiado.

## Como Rodar

### Requisitos

- Python 3.12 ou superior
- Windows recomendado

### Passos

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Na primeira execução, o sistema cria automaticamente as pastas locais de dados, backups e relatórios.

## Observação

Este projeto ainda está em beta. Ele já possui bastante coisa pronta, mas continua evoluindo conforme o uso mostra o que realmente ajuda no dia a dia.
