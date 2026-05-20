# Balcao Inteligente

Sistema desktop para controle de bar, mercearia e pequenos comercios.

Versao atual: **0.6 beta**  
Base do projeto: **Python + PyQt6 + SQLite**  
Status: em desenvolvimento, mas ja utilizavel para testes reais de rotina.

## Sobre o projeto

O Balcao Inteligente nasceu para organizar aquelas partes do comercio que costumam ficar espalhadas: estoque, cliente que compra fiado, fechamento de caixa, compras de fornecedor, relatorios e alertas.

A ideia nao e substituir a correria do balcao, e sim dar um lugar confiavel para registrar o que importa. Por isso o app tem duas formas de venda: uma mais detalhada, baixando produto do estoque, e uma venda rapida para quando so da tempo de registrar o valor no caixa.

## O que o sistema faz hoje

### Dashboard

- Mostra indicadores gerais do negocio.
- Resume clientes, produtos, valor em estoque, estoque baixo e vendas fiadas.
- Ajuda a bater o olho e entender se tem algo pedindo atencao.

### Clientes

- Cadastro, edicao e desativacao de clientes.
- Busca por nome, CPF, telefone ou email.
- Marcacao de cliente VIP.
- Historico de valor gasto e ultima compra.

### Estoque

- Cadastro completo de produtos.
- Controle de quantidade, preco de compra, preco de venda e margem.
- Entrada e saida manual de estoque.
- Categorias de produtos com criacao, edicao e exclusao definitiva.
- Avisos para produtos com estoque baixo.

### PDV

- Venda por produto com baixa automatica no estoque.
- Venda rapida por valor, pensada para a correria do atendimento.
- Registro no caixa quando a forma de pagamento entra como dinheiro, pix, cartao ou outro.
- Historico das vendas feitas pelo PDV.
- O fiado fica fora do PDV de proposito, porque precisa estar ligado a um cliente.

### Vendas fiadas

- Lancamento de venda fiada por cliente.
- Baixa automatica do estoque nos produtos vendidos.
- Controle de divida pendente, pago e inadimplente.
- Detalhamento por cliente.
- Exclusao de venda com reposicao de estoque quando a venda ja tinha baixado produto.
- Ferramenta para corrigir estoque de vendas antigas que foram registradas antes da integracao com o estoque.

### Caixa

- Abertura de caixa com saldo inicial.
- Lancamento de entradas e saidas.
- Integracao com vendas registradas pelo PDV.
- Fechamento com saldo esperado, saldo contado e diferenca.
- Historico para conferencia do movimento.

### Fornecedores e compras

- Cadastro e gerenciamento de fornecedores.
- Registro de compras por fornecedor.
- Marcacao de compra como entregue, somando os itens ao estoque.
- Protecao para nao somar a mesma compra duas vezes.
- Exclusao de compra entregue com ajuste reverso no estoque, quando possivel.
- Importacao de XML de NF-e para cadastrar ou atualizar produtos.
- Historico de XMLs importados por fornecedor.

### Relatorios e graficos

- Painel visual com resumo do negocio.
- Abas para resumo, caixa, alertas, rankings e acoes sugeridas.
- Graficos focados em decisao, como dinheiro parado em estoque e relacao entre caixa e fiado.
- Exportacao de relatorios para PDF e Excel.

### Automacoes e alertas

- Automacoes simples para acompanhar estoque baixo, fiado pendente e outras rotinas.
- Execucao periodica dentro do app.
- Alertas na barra de status.
- Backup automatico ao abrir, ao fechar e em intervalos durante o uso.

## Mudancas mais recentes da versao 0.6 beta

- Fechamento de caixa adicionado e integrado aos relatorios.
- Area de relatorios refeita para ficar mais visual e menos textual.
- Graficos reorganizados para mostrar informacoes de decisao.
- PDV criado com venda por produto e venda rapida.
- Vendas fiadas agora baixam estoque automaticamente.
- Compras entregues agora entram no estoque.
- Categorias podem ser excluidas de vez.
- Componentes visuais foram padronizados em botoes, tabelas, cards e dialogos.
- Correcoes de contraste em telas de inadimplentes e detalhes de fiado.

## Como rodar

Requisitos:

- Python 3.12 ou superior
- Windows recomendado

Passos:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Na primeira execucao, o sistema cria automaticamente as pastas locais de dados, backups e relatorios.

## Pastas e dados locais

O app usa SQLite local. Os dados reais ficam fora do Git por seguranca:

- `data/`
- `backups/`
- `relatorios/`
- `.venv/`
- `build/`
- `dist/`

Essas pastas nao devem ser enviadas para o GitHub junto com dados reais de clientes, fornecedores, caixa ou vendas.

## GitHub

Para subir o projeto:

```powershell
git add .
git commit -m "Atualiza sistema de gerenciamento"
git push origin main
```

Se for o primeiro envio da branch:

```powershell
git push -u origin main
```

Recomendacao: manter o repositorio privado enquanto o sistema estiver sendo usado em negocio real ou ainda tiver regras comerciais em desenvolvimento.

## Observacao

Este projeto ainda esta em beta. Ele ja tem bastante coisa pronta, mas continua evoluindo conforme o uso mostra o que realmente ajuda no dia a dia.
