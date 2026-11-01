from pathlib import Path

import duckdb
import streamlit as st

CAMINHO_BANCO = Path(__file__).resolve().parent / "dados_financeiros.duckdb"
LIMITE_PREVIA = 500


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def listar_tabelas() -> list[tuple[str, str]]:
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        resultado = conexao.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type IN ('BASE TABLE', 'VIEW')
              AND table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
            """
        ).fetchall()
    return [(schema, tabela) for schema, tabela in resultado]


def carregar_tabela(schema: str, tabela: str):
    nome_completo = f"{citar_identificador(schema)}.{citar_identificador(tabela)}"
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        total_registros = conexao.execute(
            f"SELECT COUNT(*) FROM {nome_completo}"
        ).fetchone()[0]
        colunas = conexao.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
            """,
            [schema, tabela],
        ).fetchall()
        dados = conexao.execute(
            f"SELECT * FROM {nome_completo} LIMIT {LIMITE_PREVIA}"
        ).fetchdf()
    return total_registros, colunas, dados


st.set_page_config(page_title="Localhost do DuckDB", layout="wide")
st.title("Localhost do DuckDB")
st.caption(f"Banco local: `{CAMINHO_BANCO.name}`")

if not CAMINHO_BANCO.is_file():
    st.error(f"Banco não encontrado: {CAMINHO_BANCO}")
    st.stop()

try:
    tabelas = listar_tabelas()
except duckdb.Error as erro:
    st.error(f"Não foi possível abrir o banco: {erro}")
    st.stop()

if not tabelas:
    st.info("Nenhuma tabela foi encontrada no banco.")
    st.stop()

camadas = sorted({schema for schema, _ in tabelas})
indice_marts = camadas.index("marts") if "marts" in camadas else 0
camada = st.sidebar.selectbox("Camada", camadas, index=indice_marts)
tabelas_da_camada = [
    tabela for schema, tabela in tabelas if schema == camada
]
tabela = st.sidebar.selectbox("Tabela", tabelas_da_camada)

try:
    total_registros, colunas, dados = carregar_tabela(camada, tabela)
except duckdb.Error as erro:
    st.error(f"Não foi possível consultar a tabela: {erro}")
    st.stop()

st.subheader(f"{camada}.{tabela}")
resumo_total, resumo_colunas = st.columns(2)
resumo_total.metric("Registros", f"{total_registros:,}".replace(",", "."))
resumo_colunas.metric("Colunas", len(colunas))

st.dataframe(dados, width="stretch", hide_index=True)
st.caption(f"Prévia limitada a {LIMITE_PREVIA} registros.")

with st.expander("Estrutura da tabela"):
    st.dataframe(
        [{"Coluna": nome, "Tipo": tipo} for nome, tipo in colunas],
        width="stretch",
        hide_index=True,
    )