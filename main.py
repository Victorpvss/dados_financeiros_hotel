from pathlib import Path

import duckdb

CAMINHO_BANCO = Path(__file__).resolve().parent / "dados_financeiros.duckdb"
LINHAS_POR_PAGINA = 30


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def listar_indicadores(
    caminho_banco: Path | None = None,
) -> list[str]:
    caminho_banco = caminho_banco or CAMINHO_BANCO
    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        return [
            nome
            for (nome,) in conexao.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'marts'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            ).fetchall()
        ]


def consultar_indicador(
    nome: str,
    limite: int = LINHAS_POR_PAGINA,
    deslocamento: int = 0,
    caminho_banco: Path | None = None,
) -> tuple[list[str], list[tuple], int]:
    caminho_banco = caminho_banco or CAMINHO_BANCO
    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        nomes_disponiveis = {
            tabela for tabela in listar_indicadores(caminho_banco)
        }
        if nome not in nomes_disponiveis:
            raise ValueError(f"Indicador nao encontrado: {nome}")

        tabela_sql = f'"marts".{citar_identificador(nome)}'
        total = conexao.execute(
            f"SELECT COUNT(*) FROM {tabela_sql}"
        ).fetchone()[0]
        ordenacao = ""
        if nome == "movimentacao_por_conta":
            ordenacao = (
                ' ORDER BY "valor_total_lancamentos" DESC, '
                '"quantidade_lancamentos" DESC, "conta_id" ASC'
            )
        resultado = conexao.execute(
            f"SELECT * FROM {tabela_sql}{ordenacao} LIMIT ? OFFSET ?",
            [limite, deslocamento],
        )
        colunas = [coluna[0] for coluna in resultado.description]
        linhas = resultado.fetchall()
    return colunas, linhas, total


def exibir_indicador(nome: str) -> None:
    _, _, total = consultar_indicador(nome, limite=0)
    for deslocamento in range(0, total, LINHAS_POR_PAGINA):
        colunas, linhas, _ = consultar_indicador(
            nome,
            limite=LINHAS_POR_PAGINA,
            deslocamento=deslocamento,
        )
        print("\t".join(colunas))
        for linha in linhas:
            print("\t".join("NULL" if valor is None else str(valor) for valor in linha))

        exibidas = deslocamento + len(linhas)
        print(f"\nExibindo {exibidas} de {total} registros.")
        if exibidas < total:
            comando = input("Enter para proxima pagina ou M para voltar ao menu: ")
            if comando.strip().lower() == "m":
                return
        else:
            input("Fim dos resultados. Pressione Enter para voltar ao menu.")


def main() -> None:
    if not CAMINHO_BANCO.is_file():
        print(f"Banco DuckDB nao encontrado: {CAMINHO_BANCO}")
        return

    while True:
        try:
            indicadores = listar_indicadores()
        except duckdb.Error as erro:
            print(f"Nao foi possivel consultar o banco: {erro}")
            return

        if not indicadores:
            print("Nenhum indicador foi encontrado no schema marts.")
            return

        print("\nIndicadores financeiros")
        for numero, indicador in enumerate(indicadores, start=1):
            nome_exibicao = indicador.replace("_", " ").capitalize()
            print(f"{numero}. {nome_exibicao}")
        print("0. Sair")

        escolha = input("Selecione um indicador: ").strip()
        if escolha == "0":
            return
        if not escolha.isdigit() or not 1 <= int(escolha) <= len(indicadores):
            print("Opcao invalida.")
            continue

        try:
            exibir_indicador(indicadores[int(escolha) - 1])
        except (duckdb.Error, ValueError) as erro:
            print(f"Nao foi possivel exibir o indicador: {erro}")


if __name__ == "__main__":
    main()