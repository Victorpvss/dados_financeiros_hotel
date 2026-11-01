SELECT
    date_trunc('month', data_aplicacao)::DATE AS mes_aplicacao,
    tipo_investimento,
    status_investimento,
    COUNT(*) AS quantidade_aplicacoes,
    SUM(valor_aplicado) AS valor_total_aplicado,
    SUM(valor_atual) AS valor_atual_total,
    ROUND(AVG(valor_aplicado), 2) AS ticket_medio_aplicacao,
    ROUND(AVG(rentabilidade_percentual), 4) AS rentabilidade_informada_media_percentual,
    ROUND(
        100.0 * (SUM(valor_atual) - SUM(valor_aplicado))
        / NULLIF(SUM(valor_aplicado), 0),
        4
    ) AS variacao_calculada_percentual
FROM refined.investimentos
GROUP BY
    date_trunc('month', data_aplicacao)::DATE,
    tipo_investimento,
    status_investimento
ORDER BY
    mes_aplicacao,
    tipo_investimento,
    status_investimento;