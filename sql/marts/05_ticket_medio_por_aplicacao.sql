SELECT
    COUNT(investimento_id) AS quantidade_aplicacoes,
    SUM(valor_aplicado) AS valor_total_aplicado,
    ROUND(AVG(valor_aplicado), 2) AS ticket_medio_por_aplicacao
FROM refined.investimentos;