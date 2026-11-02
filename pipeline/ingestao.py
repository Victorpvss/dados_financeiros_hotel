
import csv
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

ORDEM_CRIACAO = (
    "agencias",
    "cooperados",
    "contas_correntes",
    "atendimentos_relacionamento",
    "contratos_credito",
    "investimentos",
    "lancamentos_contabeis",
)

CHAVES_PRIMARIAS = {
    "agencias": "agencia_id",
    "atendimentos_relacionamento": "atendimento_id",
    "contas_correntes": "conta_id",
    "contratos_credito": "contrato_credito_id",
    "cooperados": "cooperado_id",
    "investimentos": "investimento_id",
    "lancamentos_contabeis": "lancamento_id",
}

CHAVES_ESTRANGEIRAS = {
    "cooperados": (("agencia_id", "agencias", "agencia_id"),),
    "contas_correntes": (
        ("cooperado_id", "cooperados", "cooperado_id"),
        ("agencia_id", "agencias", "agencia_id"),
    ),
    "atendimentos_relacionamento": (
        ("cooperado_id", "cooperados", "cooperado_id"),
        ("agencia_id", "agencias", "agencia_id"),
    ),
    "contratos_credito": (
        ("cooperado_id", "cooperados", "cooperado_id"),
        ("conta_id", "contas_correntes", "conta_id"),
    ),
    "investimentos": (
        ("cooperado_id", "cooperados", "cooperado_id"),
        ("conta_id", "contas_correntes", "conta_id"),
    ),
    "lancamentos_contabeis": (
        ("agencia_id", "agencias", "agencia_id"),
        ("conta_id", "contas_correntes", "conta_id"),
    ),
}


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def nome_completo_tabela(nome_tabela: str) -> str:
    return f"{citar_identificador(SCHEMA)}.{citar_identificador(nome_tabela)}"


def construir_sql_criacao(nome_tabela: str, colunas: list[str]) -> str:
    colunas_obrigatorias = {
        CHAVES_PRIMARIAS[nome_tabela],
        *(coluna for coluna, _, _ in CHAVES_ESTRANGEIRAS.get(nome_tabela, ())),
    }
    ausentes = colunas_obrigatorias - set(colunas)
    if ausentes:
        raise ValueError(
            f"Colunas de chave ausentes em {nome_tabela}: {sorted(ausentes)}"
        )

    definicoes = [f"{citar_identificador(coluna)} VARCHAR" for coluna in colunas]
    definicoes.append(
        f"PRIMARY KEY ({citar_identificador(CHAVES_PRIMARIAS[nome_tabela])})"
    )
    for coluna, tabela_pai, coluna_pai in CHAVES_ESTRANGEIRAS.get(
        nome_tabela, ()
    ):
        definicoes.append(
            f"FOREIGN KEY ({citar_identificador(coluna)}) REFERENCES "
            f"{nome_completo_tabela(tabela_pai)} "
            f"({citar_identificador(coluna_pai)})"
        )

    return (
        f"CREATE TABLE {nome_completo_tabela(nome_tabela)} "
        f"({', '.join(definicoes)})"
    )


# ============================================================
# VALIDAÇÃO DOS ARQUIVOS
# ============================================================

def validar_arquivos(pasta_raw: Path | None = None) -> None:
    """Valida a existência dos sete arquivos antes da ingestão."""
    pasta_raw = pasta_raw or PASTA_RAW

    arquivos_ausentes = [
        nome_arquivo
        for nome_arquivo in ARQUIVOS.values()
        if not (pasta_raw / nome_arquivo).is_file()
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

def executar_ingestao(
    caminho_banco: Path | None = None,
    pasta_raw: Path | None = None,
) -> dict[str, int]:
    """Carrega os CSVs em raw com PK/FK, preservando a ingestão atômica."""
    caminho_banco = caminho_banco or CAMINHO_BANCO
    pasta_raw = pasta_raw or PASTA_RAW

    # Validar todos os arquivos antes de alterar o banco.
    validar_arquivos(pasta_raw)

    conexao = duckdb.connect(str(caminho_banco))

    try:
        conexao.execute("BEGIN TRANSACTION")

        # Criar schema de origem.
        conexao.execute(
            f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"
        )

        for nome_tabela in reversed(ORDEM_CRIACAO):
            conexao.execute(
                f"DROP TABLE IF EXISTS {nome_completo_tabela(nome_tabela)}"
            )

        colunas_por_tabela = {}
        for nome_tabela in ORDEM_CRIACAO:
            caminho_arquivo = pasta_raw / ARQUIVOS[nome_tabela]
            with caminho_arquivo.open(
                encoding="utf-8-sig", newline=""
            ) as arquivo:
                colunas = next(csv.reader(arquivo), None)
            if not colunas or len(colunas) != len(set(colunas)):
                raise ValueError(
                    f"Cabecalho vazio ou com colunas duplicadas: {caminho_arquivo}"
                )
            colunas_por_tabela[nome_tabela] = colunas
            conexao.execute(construir_sql_criacao(nome_tabela, colunas))

        # A carga respeita a dependência das FKs: pais antes dos filhos.
        for nome_tabela in ORDEM_CRIACAO:
            caminho_arquivo = pasta_raw / ARQUIVOS[nome_tabela]
            colunas_sql = ", ".join(
                citar_identificador(coluna)
                for coluna in colunas_por_tabela[nome_tabela]
            )
            consulta = (
                f"INSERT INTO {nome_completo_tabela(nome_tabela)} "
                f"({colunas_sql}) SELECT * FROM read_csv("
                "?, header = true, auto_detect = true, all_varchar = true, "
                "encoding = 'utf-8')"
            )
            conexao.execute(consulta, [str(caminho_arquivo)])

        conexao.execute("COMMIT")

        # Contagem de registros após a ingestão.
        print("\nINGESTÃO CONCLUÍDA")
        print("=" * 55)

        total_registros = 0

        resultados = {}
        for nome_tabela in ORDEM_CRIACAO:

            resultado = conexao.execute(
                f"SELECT COUNT(*) FROM {nome_completo_tabela(nome_tabela)}"
            ).fetchone()

            quantidade = resultado[0]
            resultados[nome_tabela] = quantidade

            total_registros += quantidade

            print(
                f"{nome_tabela:<35} {quantidade:>10}"
            )

        print("=" * 55)
        print(f"{'TOTAL DE REGISTROS':<35} {total_registros:>10}")

        print(f"\nBanco utilizado: {caminho_banco}")
        return resultados

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
