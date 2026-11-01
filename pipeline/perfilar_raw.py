from pathlib import Path

import duckdb

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = RAIZ_PROJETO / "dados_financeiros.duckdb"
CAMINHO_RELATORIO = RAIZ_PROJETO / "relatorios" / "perfil_raw.md"
SCHEMA = "raw"


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def perfilar() -> str:
    if not CAMINHO_BANCO.is_file():
        raise FileNotFoundError(f"Banco não encontrado: {CAMINHO_BANCO}")

    linhas = [
        "# Perfil técnico do schema raw",
        "",
        "Relatório gerado por `pipeline/perfilar_raw.py`. A leitura do DuckDB é somente leitura.",
        "Os formatos são máscaras, não valores originais. Nenhuma transformação foi aplicada.",
        "",
    ]

    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        tabelas = conexao.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = ? AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """,
            [SCHEMA],
        ).fetchall()

        total_colunas = 0
        for (tabela,) in tabelas:
            tabela_sql = (
                f"{citar_identificador(SCHEMA)}."
                f"{citar_identificador(tabela)}"
            )
            total_registros = conexao.execute(
                f"SELECT COUNT(*) FROM {tabela_sql}"
            ).fetchone()[0]
            linhas_distintas = conexao.execute(
                f"SELECT COUNT(*) FROM (SELECT DISTINCT * FROM {tabela_sql})"
            ).fetchone()[0]
            duplicatas_exatas = total_registros - linhas_distintas
            colunas = conexao.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = ? AND table_name = ?
                ORDER BY ordinal_position
                """,
                [SCHEMA, tabela],
            ).fetchall()
            total_colunas += len(colunas)

            linhas.extend(
                [
                    f"## `{SCHEMA}.{tabela}`",
                    "",
                    f"- Registros: **{total_registros}**",
                    f"- Linhas duplicadas exatas: **{duplicatas_exatas}**",
                    "",
                    "| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |",
                    "|---|---:|---:|---:|---:|---:|---:|---|:---:|",
                ]
            )

            for nome_coluna, tipo in colunas:
                coluna_sql = citar_identificador(nome_coluna)
                estatisticas = conexao.execute(
                    f"""
                    SELECT
                        COUNT(*) FILTER (WHERE {coluna_sql} IS NULL),
                        COUNT(*) FILTER (
                            WHERE {coluna_sql} IS NOT NULL
                              AND TRIM({coluna_sql}) = ''
                        ),
                        COUNT(DISTINCT {coluna_sql}),
                        COUNT(*) FILTER (
                            WHERE {coluna_sql} IS NOT NULL
                              AND {coluna_sql} <> TRIM({coluna_sql})
                        ),
                        MIN(LENGTH({coluna_sql})),
                        MAX(LENGTH({coluna_sql})),
                        COUNT(DISTINCT {coluna_sql}) = COUNT(*)
                          AND COUNT(*) FILTER (WHERE {coluna_sql} IS NULL) = 0
                          AND COUNT(*) FILTER (
                              WHERE {coluna_sql} IS NOT NULL
                                AND TRIM({coluna_sql}) = ''
                          ) = 0
                    FROM {tabela_sql}
                    """
                ).fetchone()
                nulos, vazios, distintos, espacos, tamanho_min, tamanho_max, unico = estatisticas

                formatos = conexao.execute(
                    f"""
                    SELECT formato, COUNT(*) AS frequencia
                    FROM (
                        SELECT regexp_replace(
                            regexp_replace(
                                regexp_replace(
                                    {coluna_sql}, '[0-9]', '9', 'g'
                                ),
                                '[[:alpha:]]', 'A', 'g'
                            ),
                            '[^9A.,:/+%() _-]', '?', 'g'
                        ) AS formato
                        FROM {tabela_sql}
                        WHERE {coluna_sql} IS NOT NULL
                          AND TRIM({coluna_sql}) <> ''
                    )
                    GROUP BY formato
                    ORDER BY frequencia DESC, formato
                    LIMIT 3
                    """
                ).fetchall()

                resumo_formatos = "; ".join(
                    f"`{formato}` ({frequencia})"
                    for formato, frequencia in formatos
                ) or "-"
                tamanho = (
                    f"{tamanho_min or 0}-{tamanho_max or 0}"
                )
                candidato_unico = "sim" if unico else "não"

                linhas.append(
                    f"| `{nome_coluna}` | `{tipo}` | {nulos} | {vazios} | "
                    f"{distintos} | {espacos} | {tamanho} | "
                    f"{resumo_formatos} | {candidato_unico} |"
                )

            linhas.append("")

        linhas[4:4] = [
            f"Tabelas perfiladas: **{len(tabelas)}**. Colunas perfiladas: **{total_colunas}**.",
            "",
            "`Distintos` conta valores não nulos sem normalização. `Vazios` conta strings compostas apenas por espaços.",
            "`Único observado` indica unicidade nesta fotografia dos dados; não declara chave primária.",
            "",
        ]

    return "\n".join(linhas) + "\n"


def main() -> None:
    relatorio = perfilar()
    CAMINHO_RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_RELATORIO.write_text(relatorio, encoding="utf-8")
    print(f"Perfil concluído: {CAMINHO_RELATORIO}")


if __name__ == "__main__":
    main()