"""Materializa sql/marts/*.sql como tabelas no schema marts.

Regras e motivos:
- Lê apenas refined e grava apenas em marts; recria marts para remover objetos
  cujo arquivo SQL foi apagado.
- Cada arquivo SQL gera uma tabela. O nome remove o prefixo NN_; a regra de
  negócio permanece no arquivo, que só recebe o wrapper CREATE TABLE AS.
- Exibe contagens calculadas pelo DuckDB e totaliza os resultados em UTF-8.
- Valida as dependências antes de iniciar. Erros de SQL são identificados pelo
  arquivo, interrompem a execução, e marts vazio é tratado como falha porque
  pode indicar um JOIN sem correspondência.
- Toda a substituição ocorre em uma transação para preservar a última execução
  válida se qualquer etapa falhar.
"""

import re
import sys
from pathlib import Path

import duckdb

from pipeline.transformar_refined import CONVERSOES

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
CAMINHO_BANCO = RAIZ_PROJETO / "dados_financeiros.duckdb"
PASTA_SQL = RAIZ_PROJETO / "sql" / "marts"
SCHEMA_MARTS = "marts"
PREFIXO_ARQUIVO = re.compile(r"^(\d{2})_(.+)\.sql$")
TABELAS_REFINED_OBRIGATORIAS = frozenset(CONVERSOES)


class ErroMaterializacao(ValueError):
    """Erro esperado que deve ser apresentado sem traceback ao usuário."""


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def formatar_milhar(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def validar_tabelas_refined(conexao: duckdb.DuckDBPyConnection) -> None:
    tabelas_existentes = {
        tabela
        for (tabela,) in conexao.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'refined'
            """
        ).fetchall()
    }
    faltantes = sorted(TABELAS_REFINED_OBRIGATORIAS - tabelas_existentes)
    if faltantes:
        lista = ", ".join(f"refined.{tabela}" for tabela in faltantes)
        raise ErroMaterializacao(
            f"Tabelas ausentes em refined: {lista}. "
            "Rode 'uv run python -m pipeline.transformar_refined'."
        )


def descobrir_marts(pasta_sql: Path) -> list[tuple[Path, str]]:
    arquivos = sorted(pasta_sql.glob("*.sql"), key=lambda arquivo: arquivo.name)
    if not arquivos:
        raise ErroMaterializacao(f"Nenhum arquivo .sql encontrado em {pasta_sql}.")

    nomes_invalidos = []
    nomes_por_tabela: dict[str, list[str]] = {}
    marts = []
    for arquivo in arquivos:
        correspondencia = PREFIXO_ARQUIVO.fullmatch(arquivo.name)
        if not correspondencia:
            nomes_invalidos.append(arquivo.name)
            continue
        nome_tabela = correspondencia.group(2)
        marts.append((arquivo, nome_tabela))
        nomes_por_tabela.setdefault(nome_tabela.casefold(), []).append(arquivo.name)

    duplicados = [
        nomes for nomes in nomes_por_tabela.values() if len(nomes) > 1
    ]
    if nomes_invalidos or duplicados:
        partes = []
        if nomes_invalidos:
            partes.append(
                "Arquivos sem prefixo NN_: " + ", ".join(nomes_invalidos)
            )
        if duplicados:
            partes.append(
                "Arquivos com nome de tabela duplicado: "
                + "; ".join(", ".join(nomes) for nomes in duplicados)
            )
        raise ErroMaterializacao("\n".join(partes))

    return marts


def executar_marts(
    caminho_banco: Path = CAMINHO_BANCO,
    pasta_sql: Path = PASTA_SQL,
) -> list[tuple[str, int]]:
    if not caminho_banco.is_file():
        raise ErroMaterializacao(f"Banco DuckDB não encontrado: {caminho_banco}")

    try:
        conexao = duckdb.connect(str(caminho_banco))
    except duckdb.Error as erro:
        raise ErroMaterializacao(f"Falha ao abrir o banco DuckDB: {erro}") from erro

    try:
        validar_tabelas_refined(conexao)
        marts = descobrir_marts(pasta_sql)
        resultados = []

        conexao.execute("BEGIN TRANSACTION")
        try:
            conexao.execute("DROP SCHEMA IF EXISTS marts CASCADE")
            conexao.execute("CREATE SCHEMA marts")

            for arquivo, nome_tabela in marts:
                try:
                    sql = arquivo.read_text(encoding="utf-8").strip()
                    if sql.endswith(";"):
                        sql = sql[:-1].rstrip()
                    tabela_sql = (
                        f"{citar_identificador(SCHEMA_MARTS)}."
                        f"{citar_identificador(nome_tabela)}"
                    )
                    conexao.execute(f"CREATE TABLE {tabela_sql} AS {sql}")
                    quantidade = conexao.execute(
                        f"SELECT COUNT(*) FROM {tabela_sql}"
                    ).fetchone()[0]
                    if quantidade == 0:
                        raise ErroMaterializacao(
                            f"Mart marts.{nome_tabela} (arquivo {arquivo.name}) "
                            "retornou zero linhas."
                        )
                    resultados.append((nome_tabela, quantidade))
                except ErroMaterializacao:
                    raise
                except Exception as erro:
                    raise ErroMaterializacao(
                        f"Falha no arquivo {arquivo.name}: {erro}"
                    ) from erro

            conexao.execute("COMMIT")
            return resultados
        except Exception:
            conexao.execute("ROLLBACK")
            raise
    finally:
        conexao.close()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        resultados = executar_marts()
    except ErroMaterializacao as erro:
        print(erro)
        raise SystemExit(1) from erro

    total_linhas = sum(quantidade for _, quantidade in resultados)
    for nome_tabela, quantidade in resultados:
        print(
            f"✓ marts.{nome_tabela:<30} "
            f"{formatar_milhar(quantidade)} linhas"
        )
    print(
        f"Total: {len(resultados)} marts, "
        f"{formatar_milhar(total_linhas)} linhas"
    )


if __name__ == "__main__":
    main()