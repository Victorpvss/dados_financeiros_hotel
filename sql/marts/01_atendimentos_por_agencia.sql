SELECT
    a.agencia_id,
    a.nome_agencia,
    a.cidade,
    a.estado,
    COUNT(atend.atendimento_id) AS quantidade_atendimentos,
    ROUND(AVG(atend.nota_satisfacao), 2) AS media_satisfacao
FROM refined.agencias AS a
LEFT JOIN refined.atendimentos_relacionamento AS atend
    ON atend.agencia_id = a.agencia_id
GROUP BY a.agencia_id, a.nome_agencia, a.cidade, a.estado
ORDER BY quantidade_atendimentos DESC;