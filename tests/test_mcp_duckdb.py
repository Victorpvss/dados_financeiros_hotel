import json

import duckdb
import pytest

from pipeline import mcp_duckdb


@pytest.mark.parametrize(
    "sql",
    [
        "CREATE TABLE teste (id INTEGER)",
        "INSERT INTO teste VALUES (1)",
        "UPDATE teste SET id = 2",
        "DELETE FROM teste",
        "ATTACH 'outro.duckdb'",
        "SELECT 1; SELECT 2",
    ],
)
def test_validar_select_recusa_escrita_e_multiplos_statements(sql: str) -> None:
    with pytest.raises(ValueError, match="Somente uma instrução SELECT"):
        mcp_duckdb.validar_select(sql)


def test_validar_select_aceita_select_e_cte() -> None:
    assert mcp_duckdb.validar_select("SELECT 1;") == "SELECT 1"
    assert mcp_duckdb.validar_select(
        "WITH amostra AS (SELECT 1 AS valor) SELECT * FROM amostra"
    ).startswith("WITH amostra")


def test_conexao_duckdb_recusa_escrita(tmp_path, monkeypatch) -> None:
    caminho_banco = tmp_path / "somente_leitura.duckdb"
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE TABLE exemplo (valor INTEGER)")
        conexao.execute("INSERT INTO exemplo VALUES (7)")

    monkeypatch.setattr(mcp_duckdb, "CAMINHO_BANCO", caminho_banco)
    with mcp_duckdb.conectar_somente_leitura() as conexao:
        assert conexao.execute("SELECT valor FROM exemplo").fetchone() == (7,)
        with pytest.raises(duckdb.Error):
            conexao.execute("CREATE TABLE proibida (valor INTEGER)")


def test_consulta_retorna_sql_e_limita_resultado(tmp_path, monkeypatch) -> None:
    caminho_banco = tmp_path / "consulta.duckdb"
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE TABLE numeros AS SELECT range AS n FROM range(5)")

    monkeypatch.setattr(mcp_duckdb, "CAMINHO_BANCO", caminho_banco)
    sql = "SELECT n FROM numeros ORDER BY n"
    resposta = json.loads(mcp_duckdb.consultar_select(sql, limite_linhas=2))

    assert resposta["sql"] == sql
    assert resposta["sql_executada"].endswith("LIMIT 3")
    assert resposta["linhas"] == [[0], [1]]
    assert resposta["resultado_truncado"] is True
    assert resposta["somente_leitura"] is True


def test_limite_fora_da_faixa_e_recusado() -> None:
    with pytest.raises(ValueError, match="entre 1 e 500"):
        mcp_duckdb.consultar_select("SELECT 1", limite_linhas=501)