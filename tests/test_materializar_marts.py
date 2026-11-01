import duckdb
import pytest

from pipeline import materializar_marts


def preparar_banco(caminho_banco) -> None:
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE SCHEMA refined")
        for tabela in sorted(materializar_marts.TABELAS_REFINED_OBRIGATORIAS):
            conexao.execute(f'CREATE TABLE refined."{tabela}" (id INTEGER)')


def criar_schema_marts_anterior(caminho_banco) -> None:
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("CREATE SCHEMA marts")
        conexao.execute("CREATE TABLE marts.anterior AS SELECT 42 AS valor")


def consultar_tabelas_marts(caminho_banco) -> list[str]:
    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        return [
            tabela
            for (tabela,) in conexao.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'marts'
                ORDER BY table_name
                """
            ).fetchall()
        ]


def test_arquivo_select_cria_mart_e_retorna_contagem(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "00_teste.sql").write_text("SELECT 1 AS x", encoding="utf-8")
    preparar_banco(caminho_banco)

    resultado = materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert resultado == [("teste", 1)]
    assert consultar_tabelas_marts(caminho_banco) == ["teste"]


def test_arquivo_removido_remove_mart_com_outros_sql_presentes(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    arquivo_removido = pasta_sql / "00_teste.sql"
    arquivo_removido.write_text("SELECT 1 AS x", encoding="utf-8")
    (pasta_sql / "01_outro.sql").write_text("SELECT 2 AS x", encoding="utf-8")
    preparar_banco(caminho_banco)
    materializar_marts.executar_marts(caminho_banco, pasta_sql)

    arquivo_removido.unlink()
    materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == ["outro"]


def test_pasta_sem_arquivos_falha_sem_alterar_marts(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    preparar_banco(caminho_banco)
    criar_schema_marts_anterior(caminho_banco)

    with pytest.raises(materializar_marts.ErroMaterializacao, match="Nenhum arquivo"):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == ["anterior"]


def test_sql_invalido_faz_rollback_e_identifica_arquivo(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "00_quebrado.sql").write_text("SELEC invalido", encoding="utf-8")
    preparar_banco(caminho_banco)
    criar_schema_marts_anterior(caminho_banco)

    with pytest.raises(
        materializar_marts.ErroMaterializacao,
        match="00_quebrado.sql.*Parser Error",
    ):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        assert conexao.execute("SELECT valor FROM marts.anterior").fetchone() == (42,)
    assert consultar_tabelas_marts(caminho_banco) == ["anterior"]


def test_nome_sem_prefixo_e_rejeitado_sem_alterar_marts(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "teste.sql").write_text("SELECT 1 AS x", encoding="utf-8")
    preparar_banco(caminho_banco)
    criar_schema_marts_anterior(caminho_banco)

    with pytest.raises(
        materializar_marts.ErroMaterializacao,
        match="sem prefixo NN_.*teste.sql",
    ):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == ["anterior"]


def test_nomes_de_tabela_duplicados_sao_rejeitados(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "00_teste.sql").write_text("SELECT 1", encoding="utf-8")
    (pasta_sql / "01_teste.sql").write_text("SELECT 2", encoding="utf-8")
    preparar_banco(caminho_banco)
    criar_schema_marts_anterior(caminho_banco)

    with pytest.raises(
        materializar_marts.ErroMaterializacao,
        match="nome de tabela duplicado.*00_teste.sql, 01_teste.sql",
    ):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == ["anterior"]


def test_mart_vazio_faz_rollback(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "00_vazio.sql").write_text(
        "SELECT 1 AS x WHERE FALSE", encoding="utf-8"
    )
    preparar_banco(caminho_banco)
    criar_schema_marts_anterior(caminho_banco)

    with pytest.raises(materializar_marts.ErroMaterializacao, match="zero linhas"):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == ["anterior"]


def test_execucoes_repetidas_produzem_saida_identica(tmp_path, monkeypatch, capsys) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "00_teste.sql").write_text(
        "SELECT * FROM range(1001)", encoding="utf-8"
    )
    preparar_banco(caminho_banco)
    monkeypatch.setattr(materializar_marts, "CAMINHO_BANCO", caminho_banco)
    monkeypatch.setattr(materializar_marts, "PASTA_SQL", pasta_sql)

    materializar_marts.main()
    primeira_saida = capsys.readouterr().out
    materializar_marts.main()
    segunda_saida = capsys.readouterr().out

    assert primeira_saida == segunda_saida
    assert "1.001 linhas" in primeira_saida
    assert "Total: 1 marts, 1.001 linhas" in primeira_saida


def test_tabelas_refined_ausentes_sao_listadas_antes_dos_arquivos(tmp_path) -> None:
    caminho_banco = tmp_path / "teste.duckdb"
    pasta_sql = tmp_path / "sql" / "marts"
    pasta_sql.mkdir(parents=True)
    (pasta_sql / "sem_prefixo.sql").write_text("SELECT 1", encoding="utf-8")
    preparar_banco(caminho_banco)
    with duckdb.connect(str(caminho_banco)) as conexao:
        conexao.execute("DROP TABLE refined.agencias")

    with pytest.raises(
        materializar_marts.ErroMaterializacao,
        match="refined.agencias.*pipeline.transformar_refined",
    ):
        materializar_marts.executar_marts(caminho_banco, pasta_sql)

    assert consultar_tabelas_marts(caminho_banco) == []