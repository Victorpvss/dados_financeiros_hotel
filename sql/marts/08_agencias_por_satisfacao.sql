WITH avaliacao_por_agencia AS (
    SELECT
        a.agencia_id,
        a.nome_agencia,
        a.cidade,
        a.estado,
        COUNT(atend.atendimento_id) AS total_atendimentos,
        COUNT(atend.nota_satisfacao) AS quantidade_avaliacoes,
        SUM(atend.nota_satisfacao) AS soma_notas,
        ROUND(AVG(atend.nota_satisfacao), 2) AS media_satisfacao,
        ROUND(
            COALESCE(
                100.0 * COUNT(atend.nota_satisfacao)
                / NULLIF(COUNT(atend.atendimento_id), 0),
                0
            ),
            2
        ) AS percentual_atendimentos_avaliados
    FROM refined.agencias AS a
    LEFT JOIN refined.atendimentos_relacionamento AS atend
        ON atend.agencia_id = a.agencia_id
    GROUP BY
        a.agencia_id,
        a.nome_agencia,
        a.cidade,
        a.estado
),
comparacao_estadual AS (
    SELECT
        *,
        ROUND(
            SUM(soma_notas) OVER (PARTITION BY estado)
            / NULLIF(
                SUM(quantidade_avaliacoes) OVER (PARTITION BY estado),
                0
            ),
            2
        ) AS media_satisfacao_estado,
        RANK() OVER (
            PARTITION BY estado
            ORDER BY media_satisfacao DESC NULLS LAST
        ) AS posicao_no_estado
    FROM avaliacao_por_agencia
)
SELECT
    agencia_id,
    nome_agencia,
    cidade,
    estado,
    total_atendimentos,
    quantidade_avaliacoes,
    media_satisfacao,
    percentual_atendimentos_avaliados,
    media_satisfacao_estado,
    ROUND(media_satisfacao - media_satisfacao_estado, 2)
        AS diferenca_para_media_estado,
    posicao_no_estado
FROM comparacao_estadual
ORDER BY
    estado,
    media_satisfacao DESC NULLS LAST,
    quantidade_avaliacoes DESC,
    agencia_id;