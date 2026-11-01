import tempfile
from pathlib import Path

import duckdb

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = RAIZ_PROJETO / "dados_financeiros.duckdb"
PASTA_DESTINO = RAIZ_PROJETO / "refined"
SCHEMA_ORIGEM = "raw"
SCHEMA_DESTINO = "refined"

CONVERSOES = {
    "agencias": {
        "data_abertura": "DATE",
        "update_date": "TIMESTAMP",
    },
    "atendimentos_relacionamento": {
        "data_abertura": "TIMESTAMP",
        "data_encerramento": "TIMESTAMP",
        "nota_satisfacao": "SMALLINT",
        "update_date": "TIMESTAMP",
    },
    "contas_correntes": {
        "data_abertura": "DATE",
        "saldo_atual": "DECIMAL(18, 2)",
        "limite_cheque_especial": "DECIMAL(18, 2)",
        "update_date": "TIMESTAMP",
    },
    "contratos_credito": {
        "data_contratacao": "DATE",
        "valor_contratado": "DECIMAL(18, 2)",
        "taxa_juros_mensal": "DECIMAL(9, 4)",
        "quantidade_parcelas": "INTEGER",
        "valor_parcela": "DECIMAL(18, 2)",
        "saldo_devedor": "DECIMAL(18, 2)",
        "update_date": "TIMESTAMP",
    },
    "cooperados": {
        "data_nascimento": "DATE",
        "renda_mensal": "DECIMAL(18, 2)",
        "data_associacao": "DATE",
        "update_date": "TIMESTAMP",
    },
    "investimentos": {
        "data_aplicacao": "DATE",
        "data_vencimento": "DATE",
        "valor_aplicado": "DECIMAL(18, 2)",
        "valor_atual": "DECIMAL(18, 2)",
        "rentabilidade_percentual": "DECIMAL(9, 4)",
        "update_date": "TIMESTAMP",
    },
    "lancamentos_contabeis": {
        "data_lancamento": "TIMESTAMP",
        "valor_lancamento": "DECIMAL(18, 2)",
        "update_date": "TIMESTAMP",
    },
}


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def citar_literal_sql(valor: str) -> str:
    return "'" + valor.replace("'", "''") + "'"


def contar_falhas(
    conexao: duckdb.DuckDBPyConnection,
    tabela: str,
    coluna: str,
    tipo_destino: str,
) -> int:
    tabela_sql = (
        f"{citar_identificador(SCHEMA_ORIGEM)}."
        f"{citar_identificador(tabela)}"
    )
    coluna_sql = citar_identificador(coluna)
    consulta = f"""
        SELECT COUNT(*)
        FROM {tabela_sql}
        WHERE {coluna_sql} IS NOT NULL
          AND TRY_CAST({coluna_sql} AS {tipo_destino}) IS NULL
    """
    return conexao.execute(consulta).fetchone()[0]


def construir_selecao(
    conexao: duckdb.DuckDBPyConnection,
    tabela: str,
) -> str:
    tabela_sql = (
        f"{citar_identificador(SCHEMA_ORIGEM)}."
        f"{citar_identificador(tabela)}"
    )
    colunas = conexao.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = ? AND table_name = ?
        ORDER BY ordinal_position
        """,
        [SCHEMA_ORIGEM, tabela],
    ).fetchall()
    conversoes = CONVERSOES[tabela]

    expressoes = []
    for (coluna,) in colunas:
        coluna_sql = citar_identificador(coluna)
        tipo_destino = conversoes.get(coluna)
        if tipo_destino:
            expressoes.append(
                f"TRY_CAST({coluna_sql} AS {tipo_destino}) AS {coluna_sql}"
            )
        else:
            expressoes.append(coluna_sql)

    return f"SELECT {', '.join(expressoes)} FROM {tabela_sql}"


def executar_transformacao() -> dict[str, int]:
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {CAMINHO_BANCO}")

    resultados: dict[str, int] = {}
    conexao = duckdb.connect(str(CAMINHO_BANCO))
    try:
        tabelas_origem = {
            tabela
            for (tabela,) in conexao.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = ? AND table_type = 'BASE TABLE'
                """,
                [SCHEMA_ORIGEM],
            ).fetchall()
        }
        tabelas_esperadas = set(CONVERSOES)
        if tabelas_origem != tabelas_esperadas:
            faltantes = sorted(tabelas_esperadas - tabelas_origem)
            inesperadas = sorted(tabelas_origem - tabelas_esperadas)
            raise ValueError(
                "O conjunto de tabelas raw não corresponde ao mapeamento. "
                f"Ausentes: {faltantes}; inesperadas: {inesperadas}"
            )

        falhas = []
        for tabela, conversoes in CONVERSOES.items():
            for coluna, tipo_destino in conversoes.items():
                quantidade = contar_falhas(
                    conexao, tabela, coluna, tipo_destino
                )
                if quantidade:
                    falhas.append(
                        f"{tabela}.{coluna} -> {tipo_destino}: "
                        f"{quantidade} valor(es) inválido(s)"
                    )
        if falhas:
            raise ValueError(
                "Transformação cancelada; raw foi preservada. "
                "Falhas de conversão:\n- " + "\n- ".join(falhas)
            )

        with tempfile.TemporaryDirectory(
            prefix=".refined_staging_", dir=RAIZ_PROJETO
        ) as pasta_temporaria:
            arquivos_temporarios = {}
            for tabela in sorted(tabelas_esperadas):
                arquivo_temporario = Path(pasta_temporaria) / f"{tabela}.parquet"
                consulta = construir_selecao(conexao, tabela)
                caminho_sql = citar_literal_sql(str(arquivo_temporario))
                conexao.execute(
                    f"COPY ({consulta}) TO {caminho_sql} "
                    "(FORMAT PARQUET, COMPRESSION ZSTD)"
                )
                resultados[tabela] = conexao.execute(
                    f"SELECT COUNT(*) FROM read_parquet({caminho_sql})"
                ).fetchone()[0]
                arquivos_temporarios[tabela] = arquivo_temporario

            PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
            for tabela, arquivo_temporario in arquivos_temporarios.items():
                arquivo_temporario.replace(PASTA_DESTINO / f"{tabela}.parquet")

        conexao.execute("BEGIN TRANSACTION")
        try:
            conexao.execute(
                f"CREATE SCHEMA IF NOT EXISTS {citar_identificador(SCHEMA_DESTINO)}"
            )
            for tabela in sorted(tabelas_esperadas):
                tipo_objeto = conexao.execute(
                    """
                    SELECT table_type
                    FROM information_schema.tables
                    WHERE table_schema = ? AND table_name = ?
                    """,
                    [SCHEMA_DESTINO, tabela],
                ).fetchone()
                tabela_destino = (
                    f"{citar_identificador(SCHEMA_DESTINO)}."
                    f"{citar_identificador(tabela)}"
                )
                if tipo_objeto and tipo_objeto[0] == "BASE TABLE":
                    conexao.execute(f"DROP TABLE {tabela_destino}")

                caminho_parquet = citar_literal_sql(
                    str(PASTA_DESTINO / f"{tabela}.parquet")
                )
                conexao.execute(
                    f"CREATE OR REPLACE VIEW {tabela_destino} "
                    f"AS SELECT * FROM read_parquet({caminho_parquet})"
                )
            conexao.execute("COMMIT")
        except Exception:
            conexao.execute("ROLLBACK")
            raise
    finally:
        conexao.close()

    return resultados


def main() -> None:
    resultados = executar_transformacao()
    total = sum(resultados.values())
    print("TRANSFORMAÇÃO REFINED CONCLUÍDA")
    for tabela, quantidade in sorted(resultados.items()):
        print(f"{tabela:<35} {quantidade:>10} -> refined/{tabela}.parquet")
    print(f"{'TOTAL DE REGISTROS':<35} {total:>10}")
    print("Schema raw mantido sem alterações; views refined apontam para Parquet.")


if __name__ == "__main__":
    main()