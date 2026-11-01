
from pathlib import Path

import duckdb


CAMINHO_BANCO = (
    Path(__file__).resolve().parents[1]
    / "dados_financeiros.duckdb"
)


def validar_ingestao():

    conexao = duckdb.connect(
        str(CAMINHO_BANCO),
        read_only=True
    )

    try:
        consulta = """
            SELECT
                table_name,
                COUNT(*) AS total_colunas,
                SUM(
                    CASE
                        WHEN data_type != 'VARCHAR' THEN 1
                        ELSE 0
                    END
                ) AS colunas_fora_varchar
            FROM information_schema.columns
            WHERE table_schema = 'raw'
            GROUP BY table_name
            ORDER BY table_name
        """

        resultado = conexao.execute(consulta).fetchall()

        total_tabelas = conexao.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'raw'
              AND table_type = 'BASE TABLE'
        """).fetchone()[0]

        print("\nVALIDAÇÃO DA INGESTÃO")
        print("=" * 65)
        print(
            f"{'TABELA':<35}"
            f"{'COLUNAS':>12}"
            f"{'FORA VARCHAR':>18}"
        )

        for tabela, colunas, fora_varchar in resultado:
            print(
                f"{tabela:<35}"
                f"{colunas:>12}"
                f"{fora_varchar:>18}"
            )

        print("=" * 65)
        print(f"Total de tabelas: {total_tabelas}")

        aprovado = (
            total_tabelas == 7
            and len(resultado) == 7
            and all(item[2] == 0 for item in resultado)
            and all(item[1] > 0 for item in resultado)
        )

        if aprovado:
            print("\nVALIDAÇÃO APROVADA!")
        else:
            print("\nVALIDAÇÃO REPROVADA!")

    finally:
        conexao.close()


if __name__ == "__main__":
    validar_ingestao()
