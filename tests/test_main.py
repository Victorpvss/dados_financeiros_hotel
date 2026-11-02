import duckdb
import pytest

from main import consultar_indicador, listar_indicadores


def preparar_banco(caminho_banco) -> None:
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE SCHEMA marts")
        conexao.execute(
            "CREATE TABLE marts.agencias_por_satisfacao "
            "AS SELECT * FROM (VALUES (1, 'Agencia A'), (2, 'Agencia B')) "
            "AS dados(id, nome)"
        )
        conexao.execute(
            "CREATE VIEW marts.visao_teste AS SELECT 1 AS valor"
        )


def test_listar_indicadores_retorna_tabelas_ordenadas(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    preparar_banco(caminho_banco)

    resultado = listar_indicadores(caminho_banco)

    assert resultado == ["agencias_por_satisfacao"]


def test_consultar_indicador_retorna_pagina_e_total(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    preparar_banco(caminho_banco)

    colunas, linhas, total = consultar_indicador(
        "agencias_por_satisfacao",
        limite=1,
        deslocamento=1,
        caminho_banco=caminho_banco,
    )

    assert colunas == ["id", "nome"]
    assert linhas == [(2, "Agencia B")]
    assert total == 2


def test_consultar_indicador_rejeita_nome_desconhecido(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    preparar_banco(caminho_banco)

    with pytest.raises(ValueError, match="Indicador nao encontrado"):
        consultar_indicador("tabela_inexistente", caminho_banco=caminho_banco)


def test_movimentacao_por_conta_e_ordenada_da_maior_para_menor(
    tmp_path,
) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE SCHEMA marts")
        conexao.execute(
            "CREATE TABLE marts.movimentacao_por_conta "
            "(conta_id INTEGER, quantidade_lancamentos INTEGER, "
            "valor_total_lancamentos DECIMAL(12, 2))"
        )
        conexao.execute(
            "INSERT INTO marts.movimentacao_por_conta VALUES "
            "(2, 2, 100), (1, 1, 200), (3, 5, 100)"
        )

    _, linhas, _ = consultar_indicador(
        "movimentacao_por_conta", caminho_banco=caminho_banco
    )

    assert [linha[0] for linha in linhas] == [1, 3, 2]