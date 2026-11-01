SELECT
    a.agencia_id,
    a.nome_agencia,
    a.cidade,
    a.estado,
    COUNT(atend.nota_satisfacao) AS quantidade_avaliacoes,
    ROUND(AVG(atend.nota_satisfacao), 2) AS media_satisfacao
FROM refined.agencias AS a
JOIN refined.atendimentos_relacionamento AS atend
    ON atend.agencia_id = a.agencia_id
WHERE atend.nota_satisfacao IS NOT NULL
GROUP BY a.agencia_id, a.nome_agencia, a.cidade, a.estado
ORDER BY media_satisfacao DESC, quantidade_avaliacoes DESC, a.agencia_id ASC;