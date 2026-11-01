WITH movimentacao AS (
    SELECT
        conta_id,
        COUNT(*) AS quantidade_lancamentos,
        SUM(valor_lancamento) AS valor_total_lancamentos
    FROM refined.lancamentos_contabeis
    GROUP BY conta_id
)
SELECT
    cc.conta_id,
    cc.numero_conta,
    c.nome_completo,
    cc.saldo_atual,
    COALESCE(m.quantidade_lancamentos, 0) AS quantidade_lancamentos,
    COALESCE(m.valor_total_lancamentos, 0) AS valor_total_lancamentos
FROM refined.contas_correntes AS cc
JOIN refined.cooperados AS c
    ON c.cooperado_id = cc.cooperado_id
LEFT JOIN movimentacao AS m
    ON m.conta_id = cc.conta_id
ORDER BY valor_total_lancamentos DESC;