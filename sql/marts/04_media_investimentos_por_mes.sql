WITH periodo AS (
    SELECT
        date_trunc('month', MIN(data_aplicacao))::DATE AS primeiro_mes,
        date_trunc('month', MAX(data_aplicacao))::DATE AS ultimo_mes
    FROM refined.investimentos
),
calendario AS (
    SELECT unnest(generate_series(
        primeiro_mes,
        ultimo_mes,
        INTERVAL '1 month'
    ))::DATE AS mes
    FROM periodo
    WHERE primeiro_mes IS NOT NULL
),
resumo_mensal AS (
    SELECT
        date_trunc('month', data_aplicacao)::DATE AS mes,
        COUNT(*) AS quantidade_investimentos,
        COUNT(DISTINCT cooperado_id) AS cooperados_investidores,
        SUM(valor_aplicado) AS valor_total_aplicado,
        AVG(valor_aplicado) AS ticket_medio
    FROM refined.investimentos
    GROUP BY 1
),
base_mensal AS (
    SELECT
        calendario.mes,
        COALESCE(resumo_mensal.quantidade_investimentos, 0) AS quantidade_investimentos,
        COALESCE(resumo_mensal.cooperados_investidores, 0) AS cooperados_investidores,
        COALESCE(resumo_mensal.valor_total_aplicado, 0) AS valor_total_aplicado,
        resumo_mensal.ticket_medio
    FROM calendario
    LEFT JOIN resumo_mensal
        ON resumo_mensal.mes = calendario.mes
)
SELECT
    mes,
    quantidade_investimentos,
    cooperados_investidores,
    valor_total_aplicado,
    ticket_medio,
    AVG(quantidade_investimentos) OVER (
        ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS media_investimentos_por_mes,
    AVG(valor_total_aplicado) OVER (
        ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS valor_medio_aplicado_por_mes
FROM base_mensal
ORDER BY mes;