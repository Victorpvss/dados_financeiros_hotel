from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from pipeline.ingestao import executar_ingestao
from pipeline.materializar_marts import executar_marts
from pipeline.transformar_refined import executar_transformacao

CAMINHO_BANCO = Path(__file__).resolve().parent / "dados_financeiros.duckdb"
LIMITE_PREVIA = 500


def citar_identificador(nome: str) -> str:
    return '"' + nome.replace('"', '""') + '"'


def preparar_banco_se_necessario() -> None:
    if CAMINHO_BANCO.is_file():
        return
    executar_ingestao()
    executar_transformacao()
    executar_marts()


def executar_consulta(sql: str, parametros: list | None = None) -> pd.DataFrame:
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        return conexao.execute(sql, parametros or []).fetchdf()


def clausulas_filtro(
    coluna_data: str,
    coluna_estado: str,
    inicio_periodo: pd.Timestamp | None,
    estado: str | None,
) -> tuple[str, list]:
    clausulas = []
    parametros = []
    if inicio_periodo is not None:
        clausulas.append(f"CAST({coluna_data} AS DATE) >= ?")
        parametros.append(inicio_periodo.date())
    if estado:
        clausulas.append(f"{coluna_estado} = ?")
        parametros.append(estado)
    if not clausulas:
        return "", parametros
    return " WHERE " + " AND ".join(clausulas), parametros


def carregar_kpis(
    estado: str | None = None,
    inicio_investimentos: pd.Timestamp | None = None,
    inicio_satisfacao: pd.Timestamp | None = None,
    inicio_movimentacao: pd.Timestamp | None = None,
) -> dict[str, float | int]:
    filtro_investimentos, parametros_investimentos = clausulas_filtro(
        "i.data_aplicacao", "c.estado", inicio_investimentos, estado
    )
    investimento = executar_consulta(
        f"""
        SELECT
            SUM(i.valor_aplicado) AS valor_aplicado,
            SUM(i.valor_atual) AS valor_atual,
            COUNT(*) AS quantidade_aplicacoes
        FROM refined.investimentos AS i
        JOIN refined.cooperados AS c
            ON c.cooperado_id = i.cooperado_id
        {filtro_investimentos}
        """,
        parametros_investimentos,
    ).iloc[0]

    filtro_satisfacao, parametros_satisfacao = clausulas_filtro(
        "t.data_abertura", "a.estado", inicio_satisfacao, estado
    )
    satisfacao = executar_consulta(
        f"""
        SELECT
            AVG(t.nota_satisfacao) AS media_satisfacao,
            COUNT(t.nota_satisfacao) AS quantidade_avaliacoes
        FROM refined.atendimentos_relacionamento AS t
        JOIN refined.agencias AS a
            ON a.agencia_id = t.agencia_id
        {filtro_satisfacao}
          {"AND" if filtro_satisfacao else "WHERE"}
            t.nota_satisfacao IS NOT NULL
        """,
        parametros_satisfacao,
    ).iloc[0]

    filtro_movimentacao, parametros_movimentacao = clausulas_filtro(
        "l.data_lancamento", "a.estado", inicio_movimentacao, estado
    )
    movimentacao = executar_consulta(
        f"""
        SELECT
            SUM(l.valor_lancamento) AS valor_movimentado,
            COUNT(*) AS quantidade_lancamentos
        FROM refined.lancamentos_contabeis AS l
        JOIN refined.agencias AS a
            ON a.agencia_id = l.agencia_id
        {filtro_movimentacao}
        """,
        parametros_movimentacao,
    ).iloc[0]
    return {
        "valor_aplicado": float(investimento["valor_aplicado"] or 0),
        "valor_atual": float(investimento["valor_atual"] or 0),
        "quantidade_aplicacoes": int(investimento["quantidade_aplicacoes"] or 0),
        "media_satisfacao": float(satisfacao["media_satisfacao"] or 0),
        "quantidade_avaliacoes": int(satisfacao["quantidade_avaliacoes"] or 0),
        "valor_movimentado": float(movimentacao["valor_movimentado"] or 0),
        "quantidade_lancamentos": int(movimentacao["quantidade_lancamentos"] or 0),
    }


def carregar_datas_finais(
    estado: str | None = None,
) -> dict[str, pd.Timestamp | None]:
    filtro_investimentos, parametros_investimentos = clausulas_filtro(
        "i.data_aplicacao", "c.estado", None, estado
    )
    filtro_satisfacao, parametros_satisfacao = clausulas_filtro(
        "t.data_abertura", "a.estado", None, estado
    )
    filtro_movimentacao, parametros_movimentacao = clausulas_filtro(
        "l.data_lancamento", "a.estado", None, estado
    )
    resultado = executar_consulta(
        f"""
        SELECT fonte, data_final
        FROM (
            SELECT 'investimentos' AS fonte,
                   MAX(i.data_aplicacao)::DATE AS data_final
            FROM refined.investimentos AS i
            JOIN refined.cooperados AS c
                ON c.cooperado_id = i.cooperado_id
            {filtro_investimentos}
            UNION ALL
            SELECT 'satisfacao' AS fonte,
                   MAX(t.data_abertura)::DATE AS data_final
            FROM refined.atendimentos_relacionamento AS t
            JOIN refined.agencias AS a
                ON a.agencia_id = t.agencia_id
            {filtro_satisfacao}
            UNION ALL
            SELECT 'movimentacao' AS fonte,
                   MAX(l.data_lancamento)::DATE AS data_final
            FROM refined.lancamentos_contabeis AS l
            JOIN refined.agencias AS a
                ON a.agencia_id = l.agencia_id
            {filtro_movimentacao}
        )
        """,
        parametros_investimentos
        + parametros_satisfacao
        + parametros_movimentacao,
    )
    return {
        fonte: pd.Timestamp(data_final) if pd.notna(data_final) else None
        for fonte, data_final in resultado.itertuples(index=False, name=None)
    }


def calcular_inicio_periodo(
    data_final: pd.Timestamp | None,
    quantidade_meses: int | None,
) -> pd.Timestamp | None:
    if data_final is None or quantidade_meses is None:
        return None
    return data_final.to_period("M").to_timestamp() - pd.DateOffset(
        months=quantidade_meses - 1
    )


def listar_estados_agencias() -> list[str]:
    dados = executar_consulta(
        """
        SELECT DISTINCT estado
        FROM refined.agencias
        WHERE estado IS NOT NULL
        ORDER BY estado
        """
    )
    return dados["estado"].tolist()


def carregar_serie_mensal(estado: str | None = None) -> pd.DataFrame:
    filtro, parametros = clausulas_filtro(
        "i.data_aplicacao", "c.estado", None, estado
    )
    dados = executar_consulta(
        f"""
        SELECT
            date_trunc('month', i.data_aplicacao)::DATE AS mes,
            COUNT(*) AS quantidade_investimentos,
            COUNT(DISTINCT i.cooperado_id) AS cooperados_investidores,
            SUM(i.valor_aplicado) AS valor_total_aplicado
        FROM refined.investimentos AS i
        JOIN refined.cooperados AS c
            ON c.cooperado_id = i.cooperado_id
        {filtro}
        GROUP BY 1
        ORDER BY mes
        """,
        parametros,
    )
    if not dados.empty:
        dados["mes"] = pd.to_datetime(dados["mes"])
        meses = pd.date_range(dados["mes"].min(), dados["mes"].max(), freq="MS")
        dados = dados.set_index("mes").reindex(meses)
        dados.index.name = "mes"
        dados[["quantidade_investimentos", "cooperados_investidores", "valor_total_aplicado"]] = (
            dados[
                [
                    "quantidade_investimentos",
                    "cooperados_investidores",
                    "valor_total_aplicado",
                ]
            ].fillna(0)
        )
        dados["media_investimentos_por_mes"] = dados[
            "quantidade_investimentos"
        ].rolling(window=3, min_periods=1).mean()
        dados["valor_medio_aplicado_por_mes"] = dados[
            "valor_total_aplicado"
        ].rolling(window=3, min_periods=1).mean()
        dados = dados.reset_index()
    return dados


def carregar_satisfacao(
    estado: str | None = None,
    inicio_periodo: pd.Timestamp | None = None,
) -> pd.DataFrame:
    filtro, parametros = clausulas_filtro(
        "t.data_abertura", "a.estado", inicio_periodo, estado
    )
    return executar_consulta(
        f"""
        WITH resumo AS (
        SELECT
            a.nome_agencia,
            a.cidade,
            a.estado,
            COUNT(t.nota_satisfacao) AS quantidade_avaliacoes,
            SUM(t.nota_satisfacao) AS soma_notas,
            AVG(t.nota_satisfacao) AS media_satisfacao
        FROM refined.agencias AS a
        JOIN refined.atendimentos_relacionamento AS t
            ON t.agencia_id = a.agencia_id
        {filtro}
          {"AND" if filtro else "WHERE"}
            t.nota_satisfacao IS NOT NULL
        GROUP BY a.nome_agencia, a.cidade, a.estado
        )
        SELECT
            nome_agencia,
            cidade,
            estado,
            quantidade_avaliacoes,
            ROUND(media_satisfacao, 2) AS media_satisfacao,
            ROUND(
                SUM(soma_notas) OVER (PARTITION BY estado)
                / NULLIF(
                    SUM(quantidade_avaliacoes) OVER (PARTITION BY estado),
                    0
                ),
                2
            ) AS media_satisfacao_estado,
            ROUND(
                media_satisfacao
                - SUM(soma_notas) OVER (PARTITION BY estado)
                    / NULLIF(
                        SUM(quantidade_avaliacoes) OVER (PARTITION BY estado),
                        0
                    ),
                2
            ) AS diferenca_para_media_estado
        FROM resumo
        ORDER BY media_satisfacao DESC, quantidade_avaliacoes DESC
        """,
        parametros,
    )


def carregar_movimentacao(
    estado: str | None = None,
    inicio_periodo: pd.Timestamp | None = None,
) -> pd.DataFrame:
    filtro, parametros = clausulas_filtro(
        "l.data_lancamento", "a.estado", inicio_periodo, estado
    )
    return executar_consulta(
        f"""
        SELECT
            cc.numero_conta,
            c.nome_completo,
            COUNT(*) AS quantidade_lancamentos,
            SUM(l.valor_lancamento) AS valor_total_lancamentos
        FROM refined.lancamentos_contabeis AS l
        JOIN refined.contas_correntes AS cc
            ON cc.conta_id = l.conta_id
        JOIN refined.cooperados AS c
            ON c.cooperado_id = cc.cooperado_id
        JOIN refined.agencias AS a
            ON a.agencia_id = l.agencia_id
        {filtro}
        GROUP BY cc.conta_id, cc.numero_conta, c.nome_completo
        ORDER BY valor_total_lancamentos DESC,
                 quantidade_lancamentos DESC,
                 cc.conta_id ASC
        LIMIT 12
        """,
        parametros,
    )


def carregar_investimentos_por_tipo(
    estado: str | None = None,
    inicio_periodo: pd.Timestamp | None = None,
) -> pd.DataFrame:
    filtro, parametros = clausulas_filtro(
        "i.data_aplicacao", "c.estado", inicio_periodo, estado
    )
    return executar_consulta(
        f"""
        SELECT
            i.tipo_investimento,
            SUM(i.valor_aplicado) AS valor_aplicado,
            SUM(i.valor_atual) AS valor_atual,
            COUNT(*) AS quantidade_aplicacoes
        FROM refined.investimentos AS i
        JOIN refined.cooperados AS c
            ON c.cooperado_id = i.cooperado_id
        {filtro}
        GROUP BY i.tipo_investimento
        ORDER BY valor_aplicado DESC
        """,
        parametros,
    )


def listar_tabelas() -> list[tuple[str, str]]:
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        resultado = conexao.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type IN ('BASE TABLE', 'VIEW')
              AND table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
            """
        ).fetchall()
    return [(schema, tabela) for schema, tabela in resultado]


def carregar_tabela(schema: str, tabela: str):
    nome_completo = f"{citar_identificador(schema)}.{citar_identificador(tabela)}"
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        total_registros = conexao.execute(
            f"SELECT COUNT(*) FROM {nome_completo}"
        ).fetchone()[0]
        colunas = conexao.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
            """,
            [schema, tabela],
        ).fetchall()
        ordenacao = ""
        if schema == "marts" and tabela == "movimentacao_por_conta":
            ordenacao = (
                ' ORDER BY "valor_total_lancamentos" DESC, '
                '"quantidade_lancamentos" DESC, "conta_id" ASC'
            )
        dados = conexao.execute(
            f"SELECT * FROM {nome_completo}{ordenacao} "
            f"LIMIT {LIMITE_PREVIA}"
        ).fetchdf()
    return total_registros, colunas, dados


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_milhoes(valor: float) -> str:
    return f"{valor / 1_000_000:.1f}".replace(".", ",")


def formatar_inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def exibir_linhas(
    dados: pd.DataFrame,
    colunas: list[tuple[str, str, str]],
    rotulo_eixo_y: str,
) -> None:
    figura, eixo = plt.subplots(figsize=(10, 3.2), layout="constrained")
    for coluna, rotulo, cor in colunas:
        eixo.plot(
            dados.index,
            pd.to_numeric(dados[coluna], errors="coerce"),
            label=rotulo,
            color=cor,
            linewidth=2.2,
        )
    eixo.set_ylabel(rotulo_eixo_y, color="#58716b")
    eixo.tick_params(colors="#58716b", labelsize=8)
    eixo.grid(axis="y", color="#dce7e1", linewidth=0.8)
    eixo.spines[["top", "right", "left"]].set_visible(False)
    eixo.spines["bottom"].set_color("#dce7e1")
    eixo.legend(frameon=False, loc="upper left", ncol=2, fontsize=8)
    figura.autofmt_xdate(rotation=0)
    st.pyplot(figura, width="stretch")
    plt.close(figura)


def exibir_barras(
    dados: pd.DataFrame,
    coluna_valor: str,
    cor: str,
    horizontal: bool = True,
) -> None:
    valores = pd.to_numeric(dados[coluna_valor], errors="coerce").fillna(0)
    figura, eixo = plt.subplots(
        figsize=(9, max(3.2, len(dados) * 0.32)),
        layout="constrained",
    )
    if horizontal:
        eixo.barh(dados.index.astype(str), valores, color=cor, height=0.66)
        eixo.invert_yaxis()
        eixo.xaxis.grid(True, color="#dce7e1", linewidth=0.8)
        eixo.set_axisbelow(True)
        eixo.spines[["top", "right", "left"]].set_visible(False)
        eixo.spines["bottom"].set_color("#dce7e1")
    else:
        eixo.bar(dados.index.astype(str), valores, color=cor, width=0.68)
        eixo.yaxis.grid(True, color="#dce7e1", linewidth=0.8)
        eixo.set_axisbelow(True)
        eixo.spines[["top", "right", "left"]].set_visible(False)
        eixo.spines["bottom"].set_color("#dce7e1")
        eixo.tick_params(axis="x", labelrotation=25)
    eixo.tick_params(colors="#58716b", labelsize=8)
    st.pyplot(figura, width="stretch")
    plt.close(figura)


def exibir_dashboard() -> None:
    st.title("Painel financeiro")
    st.caption("Visão consolidada de investimentos, relacionamento e movimentações")

    estados = listar_estados_agencias()
    filtros = st.columns([2, 3, 5])
    estado = filtros[0].selectbox("Estado das agências", ["Todos", *estados])
    periodo = filtros[1].selectbox(
        "Período",
        ["Todo o histórico", "Últimos 12 meses", "Últimos 6 meses"],
    )
    meses_por_periodo = {
        "Últimos 6 meses": 6,
        "Últimos 12 meses": 12,
    }
    estado_filtro = None if estado == "Todos" else estado
    datas_finais = carregar_datas_finais(estado_filtro)
    if not any(datas_finais.values()):
        st.info("Não há dados para a combinação de filtros selecionada.")
        return

    quantidade_meses = meses_por_periodo.get(periodo)
    inicio_investimentos = calcular_inicio_periodo(
        datas_finais["investimentos"], quantidade_meses
    )
    inicio_satisfacao = calcular_inicio_periodo(
        datas_finais["satisfacao"], quantidade_meses
    )
    inicio_movimentacao = calcular_inicio_periodo(
        datas_finais["movimentacao"], quantidade_meses
    )
    serie = carregar_serie_mensal(estado_filtro)
    serie_filtrada = serie.copy()
    if inicio_investimentos is not None:
        serie_filtrada = serie_filtrada[
            serie_filtrada["mes"] >= inicio_investimentos
        ]

    satisfacao = carregar_satisfacao(estado_filtro, inicio_satisfacao)
    kpis = carregar_kpis(
        estado_filtro,
        inicio_investimentos,
        inicio_satisfacao,
        inicio_movimentacao,
    )

    variacao_carteira = (
        100 * (kpis["valor_atual"] - kpis["valor_aplicado"])
        / kpis["valor_aplicado"]
        if kpis["quantidade_aplicacoes"] and kpis["valor_aplicado"]
        else None
    )
    metricas = st.columns(4)
    metricas[0].metric(
        "Aplicado · R$ mi",
        formatar_milhoes(kpis["valor_aplicado"])
        if kpis["quantidade_aplicacoes"]
        else "Sem dados",
    )
    metricas[1].metric(
        "Carteira · R$ mi",
        formatar_milhoes(kpis["valor_atual"])
        if kpis["quantidade_aplicacoes"]
        else "Sem dados",
        f"{variacao_carteira:+.1f}%" if variacao_carteira is not None else None,
    )
    metricas[2].metric(
        "Satisfação",
        f"{kpis['media_satisfacao']:.2f}/10"
        if kpis["quantidade_avaliacoes"]
        else "Sem dados",
    )
    metricas[3].metric(
        "Mov. · R$ mi",
        formatar_milhoes(kpis["valor_movimentado"])
        if kpis["quantidade_lancamentos"]
        else "Sem dados",
    )
    st.caption(
        "Os filtros afetam todos os indicadores. Carteira mostra o valor atual "
        "dos investimentos aplicados no recorte selecionado."
    )

    st.divider()
    st.subheader("Investimentos ao longo do tempo")
    if serie_filtrada.empty:
        st.info("Sem investimentos no recorte selecionado.")
    else:
        graficos_tempo = st.columns(2)
        with graficos_tempo[0]:
            st.caption("Aplicações por mês e média móvel de 3 meses")
            grafico_quantidade = serie_filtrada.set_index("mes")[[
                "quantidade_investimentos",
                "media_investimentos_por_mes",
            ]]
            exibir_linhas(
                grafico_quantidade,
                [
                    ("quantidade_investimentos", "Aplicações", "#0d7c66"),
                    ("media_investimentos_por_mes", "Média móvel (3m)", "#e29b45"),
                ],
                "Aplicações",
            )
        with graficos_tempo[1]:
            st.caption("Volume aplicado e média móvel de 3 meses")
            grafico_valor = serie_filtrada.set_index("mes")[[
                "valor_total_aplicado",
                "valor_medio_aplicado_por_mes",
            ]]
            exibir_linhas(
                grafico_valor,
                [
                    ("valor_total_aplicado", "Valor aplicado", "#277da1"),
                    ("valor_medio_aplicado_por_mes", "Média móvel (3m)", "#e29b45"),
                ],
                "Reais (R$)",
            )

    st.divider()
    st.subheader("Agências e produtos")
    graficos_categoria = st.columns([1.2, 1])
    with graficos_categoria[0]:
        st.caption("Satisfação média por agência")
        if satisfacao.empty:
            st.info("Sem avaliações de satisfação no recorte selecionado.")
        else:
            dados_agencias = satisfacao.nlargest(
                10, "media_satisfacao"
            ).sort_values("media_satisfacao").set_index("nome_agencia")
            exibir_barras(dados_agencias, "media_satisfacao", "#0d7c66")
    with graficos_categoria[1]:
        st.caption("Valor aplicado por tipo de investimento")
        por_tipo = carregar_investimentos_por_tipo(
            estado_filtro, inicio_investimentos
        )
        if por_tipo.empty:
            st.info("Sem investimentos no recorte selecionado.")
        else:
            dados_tipos = por_tipo.set_index("tipo_investimento")
            exibir_barras(dados_tipos, "valor_aplicado", "#277da1")

    st.divider()
    st.subheader("Contas com maior movimentação")
    movimentacao = carregar_movimentacao(estado_filtro, inicio_movimentacao)
    if movimentacao.empty:
        st.info("Sem movimentações no recorte selecionado.")
    else:
        movimentacao_exibicao = movimentacao.copy()
        movimentacao_exibicao["valor_total_lancamentos"] = movimentacao_exibicao[
            "valor_total_lancamentos"
        ].astype(float)
        movimentacao_exibicao["conta_exibicao"] = (
            movimentacao_exibicao["numero_conta"]
            + " · "
            + movimentacao_exibicao["nome_completo"]
        )
        tabela_grafico = movimentacao_exibicao.set_index("conta_exibicao")[[
            "valor_total_lancamentos"
        ]].sort_values("valor_total_lancamentos", ascending=True)
        exibir_barras(tabela_grafico, "valor_total_lancamentos", "#d87855")
        st.dataframe(
            movimentacao,
            width="stretch",
            hide_index=True,
            column_config={
                "valor_total_lancamentos": st.column_config.NumberColumn(
                    "Total movimentado", format="R$ %.2f"
                ),
                "quantidade_lancamentos": st.column_config.NumberColumn(
                    "Lançamentos", format="localized"
                ),
            },
        )


def exibir_explorador(tabelas: list[tuple[str, str]]) -> None:
    st.title("Explorador de dados")
    st.caption("Prévia das tabelas e views disponíveis no DuckDB")
    camadas = sorted({schema for schema, _ in tabelas})
    indice_marts = camadas.index("marts") if "marts" in camadas else 0
    camada = st.selectbox("Camada", camadas, index=indice_marts)
    tabelas_da_camada = [tabela for schema, tabela in tabelas if schema == camada]
    tabela = st.selectbox("Tabela", tabelas_da_camada)
    total_registros, colunas, dados = carregar_tabela(camada, tabela)

    resumo_total, resumo_colunas = st.columns(2)
    resumo_total.metric("Registros", formatar_inteiro(total_registros))
    resumo_colunas.metric("Colunas", len(colunas))
    st.dataframe(dados, width="stretch", hide_index=True)
    st.caption(f"Prévia limitada a {LIMITE_PREVIA} registros.")
    with st.expander("Estrutura da tabela"):
        st.dataframe(
            [{"Coluna": nome, "Tipo": tipo} for nome, tipo in colunas],
            width="stretch",
            hide_index=True,
        )


def main() -> None:
    st.set_page_config(page_title="Painel financeiro | Cooperativa", layout="wide")
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f3f7f4 0%, #fbfaf6 58%, #f3f6f7 100%); color: #203b35; }
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"],
    [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] { color: #203b35 !important; }
    [data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #35534b !important; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: #173b35; }
    [data-testid="stHeader"] { background: rgba(243, 247, 244, .92); }
    [data-testid="stMetric"] { background: rgba(255,255,255,.82); border: 1px solid #dce7e1; border-top: 3px solid #0d7c66; padding: 18px 20px; border-radius: 6px; }
    [data-testid="stMetricLabel"] { color: #58716b; }
    [data-testid="stMetricValue"] { color: #173b35; font-family: 'Manrope', sans-serif; font-size: 1.45rem; }
    [data-testid="stSidebar"] { background: #e8f0eb; border-right: 1px solid #d4e0d9; }
    </style>
        """,
        unsafe_allow_html=True,
    )

    if not CAMINHO_BANCO.is_file():
        try:
            with st.spinner("Preparando os dados do dashboard..."):
                preparar_banco_se_necessario()
        except (duckdb.Error, OSError, ValueError) as erro:
            st.error(f"Não foi possível preparar o banco do dashboard: {erro}")
            st.stop()

    try:
        tabelas_disponiveis = listar_tabelas()
    except duckdb.Error as erro:
        st.error(f"Não foi possível abrir o banco: {erro}")
        st.stop()

    if not tabelas_disponiveis:
        st.info("Nenhuma tabela foi encontrada no banco.")
        st.stop()

    st.sidebar.title("Cooperativa")
    st.sidebar.caption("INTELIGÊNCIA FINANCEIRA")
    tela = st.sidebar.radio("Navegação", ["Visão geral", "Explorador de dados"])
    st.sidebar.divider()
    st.sidebar.caption(f"Banco local · {CAMINHO_BANCO.name}")

    try:
        if tela == "Visão geral":
            exibir_dashboard()
        else:
            exibir_explorador(tabelas_disponiveis)
    except duckdb.Error as erro:
        st.error(f"Não foi possível carregar os indicadores: {erro}")


if __name__ == "__main__":
    main()