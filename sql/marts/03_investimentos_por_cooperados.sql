WITH resumo_investimentos AS (
    SELECT
        cooperado_id,
        COUNT(*) AS quantidade_investimentos,
        SUM(valor_aplicado) AS total_aplicado,
        SUM(valor_atual) AS valor_atual_total
    FROM refined.investimentos
    GROUP BY cooperado_id
)
SELECT
    c.cooperado_id,
    c.nome_completo,
    COALESCE(ri.quantidade_investimentos, 0) AS quantidade_investimentos,
    COALESCE(ri.total_aplicado, 0) AS total_aplicado,
    COALESCE(ri.valor_atual_total, 0) AS valor_atual_total
FROM refined.cooperados AS c
LEFT JOIN resumo_investimentos AS ri
    ON ri.cooperado_id = c.cooperado_id
ORDER BY total_aplicado DESC;