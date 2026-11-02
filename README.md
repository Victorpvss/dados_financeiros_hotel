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

Para regenerar os dados fictícios com distribuições mais variadas, execute
antes da ingestão:

```powershell
uv run python -m pipeline.gerar_dados_sinteticos
```

O gerador atualiza `fonte_dados/` e `raw/` com a mesma semente fixa
(`20261102`), preserva cabeçalhos, contagens e identificadores, e produz os
mesmos valores a cada execução para facilitar a reprodução dos resultados.
As aplicações de investimento incluem sazonalidade e meses de campanha; o
indicador mensal apresenta médias móveis de três meses para quantidade e valor.
Em seguida, execute novamente o pipeline na ordem acima para atualizar o banco,
os arquivos refined e os indicadores.

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

O modelo representa dados financeiros de uma cooperativa, não um sistema de
vendas. As sete tabelas de origem representam agências, atendimentos, contas
correntes, contratos de crédito, cooperados, investimentos e lançamentos
contábeis.

A ingestão impõe chaves primárias nas sete tabelas de `raw` e chaves estrangeiras
para as relações existentes entre agências, cooperados, contas, atendimentos,
contratos, investimentos e lançamentos. A carga é transacional: IDs duplicados
ou referências inexistentes cancelam a ingestão sem substituir a versão válida
anterior. As colunas raw continuam textuais para preservar os valores de origem.
`refined` aplica tipos e lê arquivos Parquet por meio de views; os marts são
resultados derivados e recriáveis. `produto_credito_id` permanece sem FK porque
este conjunto de dados não contém uma tabela de produtos de crédito.

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