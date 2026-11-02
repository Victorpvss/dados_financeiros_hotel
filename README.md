# Projeto de Análise de Dados Financeiros

Pipeline de dados financeiros de uma cooperativa, da ingestão de arquivos CSV
até a geração de indicadores analíticos consultáveis no DuckDB. O repositório
também inclui um menu de terminal, uma interface Streamlit e testes automatizados.

## Requisitos

- Python 3.12 ou superior.
- [uv](https://docs.astral.sh/uv/) para instalar as dependências e executar os
  comandos do projeto. Também é possível instalar com `pip` usando
  `requirements.txt`.

## Instalação

Na raiz do repositório, execute:

```powershell
uv sync --all-groups
```

Alternativamente, crie e ative um ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Executar o pipeline

Os arquivos de origem ficam em `raw/`. Execute as etapas abaixo, na ordem,
sempre a partir da raiz do projeto:

```powershell
uv run python -m pipeline.ingestao
uv run python -m pipeline.validar_ingestao
uv run python -m pipeline.perfilar_raw
uv run python -m pipeline.transformar_refined
uv run python -m pipeline.materializar_marts
```

O banco `dados_financeiros.duckdb` é criado ou atualizado no diretório raiz.
As consultas em `sql/marts/` são materializadas como tabelas no schema `marts`.
O materializador recria esse schema em uma transação; portanto, alterações
manuais nesse schema não são preservadas ao executar novamente o pipeline.

## Consultar os indicadores

Menu de terminal:

```powershell
uv run python main.py
```

Interface Streamlit para navegar pelos schemas e visualizar tabelas:

```powershell
uv run streamlit run ui.py
```

## Testes e lint

```powershell
uv run pytest
uv run ruff check .
```

## Organização e modelo de dados

- `fonte_dados/`: arquivos fornecidos como fonte.
- `raw/`: CSVs usados pela ingestão.
- `pipeline/`: ingestão, validação, perfilamento, transformação e materialização.
- `refined/`: arquivos Parquet tipados; no DuckDB, as tabelas desse schema são
  views sobre esses arquivos.
- `sql/marts/`: consultas dos indicadores analíticos.
- `tests/`: testes automatizados.

O modelo representa um fluxo analítico, não um sistema transacional de vendas.
As sete tabelas de origem representam agências, atendimentos, contas correntes,
contratos de crédito, cooperados, investimentos e lançamentos contábeis. As
relações de negócio são expressas pelos identificadores usados nos `JOINs` das
consultas.

As camadas `raw` e `refined` preservam a estrutura dos dados recebidos e a
transformação de tipos, enquanto `marts` contém resultados derivados e
recriáveis. Por esse motivo, as tabelas são carregadas sem declarar constraints
de `PRIMARY KEY` e `FOREIGN KEY`; a existência de identificadores nas fontes não
significa que o banco imponha essas constraints. Este desenho é apropriado ao
pipeline analítico, mas não equivale a um modelo relacional transacional com
integridade referencial aplicada.

## Escolha do banco e compatibilidade com o desafio

O projeto usa DuckDB para consultas analíticas locais sobre CSV, Parquet e
tabelas agregadas. DuckDB e SQLite são tecnologias diferentes. O requisito do
desafio menciona especificamente o módulo `sqlite3`; portanto, este projeto só
atende a esse item se a pessoa responsável pela avaliação aceitar DuckDB como
alternativa. Essa aceitação não pode ser inferida apenas pelo código e deve ser
confirmada com a organização do desafio.

## Dependências

As dependências e suas versões mínimas são mantidas em `pyproject.toml`. O
`requirements.txt` oferece uma lista compatível com instalações via `pip`.