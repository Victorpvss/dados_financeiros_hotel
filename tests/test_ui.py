import pandas as pd

import ui
from ui import calcular_inicio_periodo


def test_calcular_inicio_periodo_usa_data_final_da_fonte() -> None:
    data_final = pd.Timestamp("2026-10-12")

    resultado = calcular_inicio_periodo(data_final, 6)

    assert resultado == pd.Timestamp("2026-05-01")


def test_calcular_inicio_periodo_sem_limite_retorna_none() -> None:
    assert calcular_inicio_periodo(pd.Timestamp("2026-10-12"), None) is None
    assert calcular_inicio_periodo(None, 6) is None


def test_preparar_banco_executa_pipeline_quando_banco_nao_existe(
    tmp_path, monkeypatch
) -> None:
    chamadas = []
    monkeypatch.setattr(ui, "CAMINHO_BANCO", tmp_path / "dashboard.duckdb")
    monkeypatch.setattr(ui, "executar_ingestao", lambda: chamadas.append("raw"))
    monkeypatch.setattr(
        ui, "executar_transformacao", lambda: chamadas.append("refined")
    )
    monkeypatch.setattr(ui, "executar_marts", lambda: chamadas.append("marts"))

    ui.preparar_banco_se_necessario()

    assert chamadas == ["raw", "refined", "marts"]


def test_preparar_banco_nao_refaz_pipeline_se_banco_existe(
    tmp_path, monkeypatch
) -> None:
    caminho_banco = tmp_path / "dashboard.duckdb"
    caminho_banco.touch()
    chamadas = []
    monkeypatch.setattr(ui, "CAMINHO_BANCO", caminho_banco)
    monkeypatch.setattr(ui, "executar_ingestao", lambda: chamadas.append("raw"))

    ui.preparar_banco_se_necessario()

    assert chamadas == []