# Gerenciamento Casa Guarani

Sistema desktop em Python/PyQt6 para gerenciamento de bar e mercearia.

## Funcionalidades

- Dashboard com indicadores do negocio
- Clientes, estoque, categorias e fornecedores
- Importacao de XML de NF-e para produtos/fornecedores
- Vendas fiadas com inadimplentes e historico
- PDV opcional com venda por produto e venda rapida
- Fechamento de caixa e movimentacoes
- Relatorios, rankings e graficos de decisao
- Automacoes simples para alertas, fiado, estoque e backups
- Exportacao de relatorios em PDF e Excel

## Como rodar

Requisitos:

- Python 3.12 ou superior
- Windows recomendado para uso local

Passos:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Na primeira execucao o sistema cria automaticamente as pastas `data`, `backups` e `relatorios`, alem do banco SQLite local.

## Dados locais

Arquivos de banco, backups e relatorios gerados pelo app nao devem ser enviados ao GitHub. Eles ficam ignorados pelo `.gitignore`:

- `data/`
- `backups/`
- `relatorios/`

As pastas possuem `.gitkeep` apenas para manter a estrutura no repositorio.

## Subir para o GitHub

Depois de instalar o Git ou abrir pelo GitHub Desktop, suba somente os arquivos do projeto:

```powershell
git init
git add .
git commit -m "Versao inicial do sistema"
git branch -M main
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```

Recomendacao: use repositorio privado enquanto o sistema ainda tiver dados e regras de negocio em evolucao.

## Observacoes

Este projeto ainda esta em evolucao. Antes de publicar publicamente, revise se nao existem dados reais de clientes, fornecedores, caixa ou vendas dentro da pasta.
