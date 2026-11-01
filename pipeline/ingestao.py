
from pathlib import Path

import duckdb


# ============================================================
# CONFIGURAÇÕES
# ============================================================

RAIZ_PROJETO = Path(__file__).resolve().parents[1]

PASTA_RAW = RAIZ_PROJETO / "raw"

CAMINHO_BANCO = RAIZ_PROJETO / "dados_financeiros.duckdb"

SCHEMA = "raw"


# ============================================================
# ARQUIVOS E TABELAS
# ============================================================

ARQUIVOS = {
    "agencias": "agencias.csv",
    "atendimentos_relacionamento": "atendimentos_relacionamento.csv",
    "contas_correntes": "contas_correntes.csv",
    "contratos_credito": "contratos_credito.csv",
    "cooperados": "cooperados.csv",
    "investimentos": "investimentos.csv",
    "lancamentos_contabeis": "lancamentos_contabeis.csv",
}


# ============================================================
# VALIDAÇÃO DOS ARQUIVOS
# ============================================================

def validar_arquivos() -> None:
    """Valida a existência dos sete arquivos antes da ingestão."""

    arquivos_ausentes = [
        nome_arquivo
        for nome_arquivo in ARQUIVOS.values()
        if not (PASTA_RAW / nome_arquivo).is_file()
    ]

    if arquivos_ausentes:
        mensagem = "\n".join(
            f"- {arquivo}" for arquivo in arquivos_ausentes
        )

        raise FileNotFoundError(
            "Ingestão cancelada. Arquivos ausentes:\n"
            f"{mensagem}"
        )


# ============================================================
# INGESTÃO
# ============================================================

def executar_ingestao() -> None:
    """Realiza a ingestão dos sete arquivos CSV no DuckDB."""

    # Validar todos os arquivos antes de alterar o banco.
    validar_arquivos()

    conexao = duckdb.connect(str(CAMINHO_BANCO))

    try:
        conexao.execute("BEGIN TRANSACTION")

        # Criar schema de origem.
        conexao.execute(
            f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"
        )

        # Recriar as sete tabelas.
        for nome_tabela, nome_arquivo in ARQUIVOS.items():

            caminho_arquivo = PASTA_RAW / nome_arquivo

            consulta = f"""
                CREATE OR REPLACE TABLE {SCHEMA}.{nome_tabela} AS
                SELECT *
                FROM read_csv(
                    ?,
                    header = true,
                    auto_detect = true,
                    all_varchar = true,
                    encoding = 'utf-8'
                )
            """

            conexao.execute(
                consulta,
                [str(caminho_arquivo)]
            )

        conexao.execute("COMMIT")

        # Contagem de registros após a ingestão.
        print("\nINGESTÃO CONCLUÍDA")
        print("=" * 55)

        total_registros = 0

        for nome_tabela in ARQUIVOS:

            resultado = conexao.execute(
                f"SELECT COUNT(*) FROM {SCHEMA}.{nome_tabela}"
            ).fetchone()

            quantidade = resultado[0]

            total_registros += quantidade

            print(
                f"{nome_tabela:<35} {quantidade:>10}"
            )

        print("=" * 55)
        print(f"{'TOTAL DE REGISTROS':<35} {total_registros:>10}")

        print(f"\nBanco utilizado: {CAMINHO_BANCO}")

    except Exception:
        conexao.execute("ROLLBACK")
        raise

    finally:
        conexao.close()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    executar_ingestao()
