import csv

import duckdb
import pytest

from pipeline.ingestao import ARQUIVOS, executar_ingestao


def criar_csvs(pasta_raw, violacao: str | None = None) -> None:
    dados = {
        "agencias": (
            ["agencia_id", "nome_agencia"],
            [["1", "Agencia Um"]],
        ),
        "cooperados": (
            ["cooperado_id", "agencia_id", "nome_completo"],
            [["1", "1", "Cooperado Um"]],
        ),
        "contas_correntes": (
            ["conta_id", "cooperado_id", "agencia_id"],
            [["1", "1", "1"]],
        ),
        "atendimentos_relacionamento": (
            ["atendimento_id", "cooperado_id", "agencia_id"],
            [["1", "1", "1"]],
        ),
        "contratos_credito": (
            ["contrato_credito_id", "cooperado_id", "conta_id"],
            [["1", "1", "1"]],
        ),
        "investimentos": (
            ["investimento_id", "cooperado_id", "conta_id"],
            [["1", "1", "1"]],
        ),
        "lancamentos_contabeis": (
            ["lancamento_id", "agencia_id", "conta_id"],
            [["1", "1", "1"]],
        ),
    }
    if violacao == "primary_key":
        dados["agencias"][1].append(["1", "Agencia Duplicada"])
    elif violacao == "foreign_key":
        dados["cooperados"][1][0][1] = "999"

    pasta_raw.mkdir(parents=True, exist_ok=True)
    for tabela, arquivo in ARQUIVOS.items():
        colunas, linhas = dados[tabela]
        with (pasta_raw / arquivo).open(
            "w", encoding="utf-8", newline=""
        ) as csv_file:
            escritor = csv.writer(csv_file)
            escritor.writerow(colunas)
            escritor.writerows(linhas)


def criar_raw_anterior(caminho_banco) -> None:
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE SCHEMA raw")
        conexao.execute(
            "CREATE TABLE raw.agencias (agencia_id VARCHAR, nome_agencia VARCHAR)"
        )
        conexao.execute("INSERT INTO raw.agencias VALUES ('antiga', 'Preservada')")


@pytest.mark.parametrize("violacao", ["primary_key", "foreign_key"])
def test_violacao_de_chave_faz_rollback(tmp_path, violacao: str) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_raw = tmp_path / "raw"
    criar_csvs(pasta_raw, violacao)
    criar_raw_anterior(caminho_banco)

    with pytest.raises(duckdb.ConstraintException):
        executar_ingestao(caminho_banco, pasta_raw)

    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        assert conexao.execute(
            "SELECT * FROM raw.agencias"
        ).fetchall() == [("antiga", "Preservada")]
        tabelas = conexao.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'raw' ORDER BY table_name"
        ).fetchall()
    assert tabelas == [("agencias",)]


def test_ingestao_cria_chaves_primarias_e_estrangeiras(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_raw = tmp_path / "raw"
    criar_csvs(pasta_raw)

    resultados = executar_ingestao(caminho_banco, pasta_raw)

    assert resultados == dict.fromkeys(ARQUIVOS, 1)
    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        constraints = conexao.execute(
            "SELECT constraint_type, COUNT(*) "
            "FROM duckdb_constraints() "
            "WHERE schema_name = 'raw' GROUP BY constraint_type"
        ).fetchall()
    assert dict(constraints)["PRIMARY KEY"] == 7
    assert dict(constraints)["FOREIGN KEY"] == 11