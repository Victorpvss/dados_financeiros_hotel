import json
from pathlib import Path
from typing import Any

import duckdb
from mcp.server import MCPServer
from mcp.types import ToolAnnotations

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = Path(
    __import__("os").environ.get(
        "DUCKDB_PATH", str(RAIZ_PROJETO / "dados_financeiros.duckdb")
    )
).resolve()
SCHEMAS_PERMITIDOS = ("raw", "refined")
LIMITE_MAXIMO_LINHAS = 500

mcp = MCPServer(
    "duckdb-readonly",
    instructions=(
        "Acesse somente o banco DuckDB do projeto por ferramentas read-only. "
        "As ferramentas de consulta aceitam apenas uma instrução SELECT e "
        "incluem a SQL na resposta. Nunca trate consultas do chat como código "
        "persistente: transformações duráveis devem ser implementadas no "
        "pipeline e salvar arquivos refined/."
    ),
)

ANOTACOES_LEITURA = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
)


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def conectar_somente_leitura() -> duckdb.DuckDBPyConnection:
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(f"Banco DuckDB não encontrado: {CAMINHO_BANCO}")
    return duckdb.connect(str(CAMINHO_BANCO), read_only=True)


def serializar_resposta(
    sql: str,
    dados: dict[str, Any],
    sql_executada: str | None = None,
) -> str:
    resposta = {
        "somente_leitura": True,
        "sql": sql,
        **dados,
    }
    if sql_executada is not None:
        resposta["sql_executada"] = sql_executada
    return json.dumps(resposta, ensure_ascii=False, default=str)


def validar_select(sql: str) -> str:
    instrucoes = duckdb.extract_statements(sql)
    if len(instrucoes) != 1 or instrucoes[0].type != duckdb.StatementType.SELECT:
        raise ValueError(
            "Somente uma instrução SELECT é permitida. "
            "DDL, escrita, comandos e múltiplas instruções são recusados."
        )

    consulta = sql.strip()
    if consulta.endswith(";"):
        consulta = consulta[:-1].rstrip()
    return consulta


@mcp.tool(
    annotations=ANOTACOES_LEITURA,
    meta={"anthropic/requiresUserInteraction": True},
)
def listar_tabelas() -> str:
    """Lista tabelas e views dos schemas raw e refined, incluindo a SQL executada."""
    sql = """
        SELECT table_schema, table_name, table_type
        FROM information_schema.tables
        WHERE table_schema IN ('raw', 'refined')
        ORDER BY table_schema, table_name
    """.strip()
    with conectar_somente_leitura() as conexao:
        registros = conexao.execute(sql).fetchall()
    return serializar_resposta(
        sql,
        {
            "colunas": ["schema", "tabela", "tipo_objeto"],
            "linhas": registros,
            "total_linhas": len(registros),
        },
    )


@mcp.tool(
    annotations=ANOTACOES_LEITURA,
    meta={"anthropic/requiresUserInteraction": True},
)
def descrever_tabela(schema: str, tabela: str) -> str:
    """Retorna colunas e tipos de uma tabela raw/refined, com a SQL executada."""
    if schema not in SCHEMAS_PERMITIDOS:
        raise ValueError(f"Schema não permitido. Use: {', '.join(SCHEMAS_PERMITIDOS)}")

    sql = """
        SELECT ordinal_position, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = ? AND table_name = ?
        ORDER BY ordinal_position
    """.strip()
    with conectar_somente_leitura() as conexao:
        registros = conexao.execute(sql, [schema, tabela]).fetchall()
    if not registros:
        raise ValueError(f"Tabela não encontrada: {schema}.{tabela}")
    return serializar_resposta(
        sql,
        {
            "parametros": {"schema": schema, "tabela": tabela},
            "colunas": ["ordem", "coluna", "tipo", "aceita_nulo"],
            "linhas": registros,
            "total_colunas": len(registros),
        },
    )


@mcp.tool(
    annotations=ANOTACOES_LEITURA,
    meta={"anthropic/requiresUserInteraction": True},
)
def consultar_select(sql: str, limite_linhas: int = 100) -> str:
    """Executa uma única SELECT em raw/refined; mostra a SQL e limita resultados a 500 linhas."""
    if not 1 <= limite_linhas <= LIMITE_MAXIMO_LINHAS:
        raise ValueError(
            f"limite_linhas deve estar entre 1 e {LIMITE_MAXIMO_LINHAS}."
        )

    consulta = validar_select(sql)
    sql_executada = (
        f"SELECT * FROM ({consulta}) AS _mcp_resultado "
        f"LIMIT {limite_linhas + 1}"
    )
    with conectar_somente_leitura() as conexao:
        resultado = conexao.execute(sql_executada)
        nomes_colunas = [coluna[0] for coluna in resultado.description]
        linhas = resultado.fetchmany(limite_linhas + 1)

    truncado = len(linhas) > limite_linhas
    linhas = linhas[:limite_linhas]
    return serializar_resposta(
        sql,
        {
            "sql_executada": sql_executada,
            "colunas": nomes_colunas,
            "linhas": linhas,
            "total_linhas_retornadas": len(linhas),
            "resultado_truncado": truncado,
        },
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")