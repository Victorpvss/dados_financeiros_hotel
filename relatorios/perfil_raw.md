# Perfil técnico do schema raw

Relatório gerado por `pipeline/perfilar_raw.py`. A leitura do DuckDB é somente leitura.
Os formatos são máscaras, não valores originais. Nenhuma transformação foi aplicada.
Tabelas perfiladas: **7**. Colunas perfiladas: **84**.

`Distintos` conta valores não nulos sem normalização. `Vazios` conta strings compostas apenas por espaços.
`Único observado` indica unicidade nesta fotografia dos dados; não declara chave primária.


## `raw.agencias`

- Registros: **25**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (16); `9` (9) | sim |
| `codigo_agencia` | `VARCHAR` | 0 | 0 | 25 | 0 | 4-4 | `9999` (25) | sim |
| `nome_agencia` | `VARCHAR` | 0 | 0 | 25 | 0 | 24-24 | `AA?AAAA AAAAAAAAAAA 9999` (25) | sim |
| `cidade` | `VARCHAR` | 0 | 0 | 10 | 0 | 6-22 | `AAAAAAAA` (5); `AAAA AAA AAAAA` (3); `AAAAA AA AAAAAAA` (3) | não |
| `estado` | `VARCHAR` | 0 | 0 | 1 | 0 | 2-2 | `AA` (25) | não |
| `regiao` | `VARCHAR` | 0 | 0 | 1 | 0 | 8-8 | `AAAAAAAA` (25) | não |
| `status_agencia` | `VARCHAR` | 0 | 0 | 2 | 0 | 5-7 | `AAAAA` (23); `AAAAAAA` (2) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 25 | 0 | 10-10 | `9999-99-99` (25) | sim |
| `update_date` | `VARCHAR` | 0 | 0 | 25 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (25) | sim |

## `raw.atendimentos_relacionamento`

- Registros: **60000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `atendimento_id` | `VARCHAR` | 0 | 0 | 60000 | 0 | 1-5 | `99999` (50001); `9999` (9000); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 20000 | 0 | 1-5 | `99999` (30003); `9999` (27000); `999` (2700) | não |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (38400); `9` (21600) | não |
| `canal_atendimento` | `VARCHAR` | 0 | 0 | 5 | 0 | 3-16 | `AAAAAAAA` (24000); `AAA` (12000); `AAAAAAAAAA` (12000) | não |
| `motivo_atendimento` | `VARCHAR` | 0 | 0 | 8 | 0 | 3-21 | `AAA` (7500); `AAAAAAAA` (7500); `AAAAAAAAAA` (7500) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 36000 | 0 | 19-19 | `9999-99-99 99:99:99` (60000) | não |
| `data_encerramento` | `VARCHAR` | 4615 | 0 | 35077 | 0 | 19-19 | `9999-99-99 99:99:99` (55385) | não |
| `status_atendimento` | `VARCHAR` | 0 | 0 | 3 | 0 | 9-9 | `AAAAAAAAA` (55385); `AA_AAAAAA` (4615) | não |
| `nota_satisfacao` | `VARCHAR` | 4615 | 0 | 10 | 0 | 1-2 | `9` (49847); `99` (5538) | não |
| `descricao_resumida` | `VARCHAR` | 0 | 0 | 60000 | 0 | 84-88 | `AAAAAAAAAAA AAAA?AAA AAAAAA AAAA AAAAAA??A AA AAAAAAAAAAAAAA AAAAAAAAAAA. AAAAAAAA 99999` (50001); `AAAAAAAAAAA AAAA?AAA AAAAAA AAAA AAAAAA??A AA AAAAAAAAAAAAAA AAAAAAAAAAA. AAAAAAAA 9999` (9000); `AAAAAAAAAAA AAAA?AAA AAAAAA AAAA AAAAAA??A AA AAAAAAAAAAAAAA AAAAAAAAAAA. AAAAAAAA 999` (900) | sim |
| `update_date` | `VARCHAR` | 0 | 0 | 25 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (60000) | não |

## `raw.contas_correntes`

- Registros: **22000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `conta_id` | `VARCHAR` | 0 | 0 | 22000 | 0 | 1-5 | `99999` (12001); `9999` (9000); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 20000 | 0 | 1-5 | `9999` (10001); `99999` (10001); `999` (1800) | não |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (14080); `9` (7920) | não |
| `numero_conta` | `VARCHAR` | 0 | 0 | 22000 | 0 | 13-13 | `9999-99999999` (22000) | sim |
| `tipo_conta` | `VARCHAR` | 0 | 0 | 3 | 0 | 14-17 | `AAAAA_AAAAAAAA_AA` (18000); `AAAAA_AAAAAAAA` (4000) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 300 | 0 | 10-10 | `9999-99-99` (22000) | não |
| `saldo_atual` | `VARCHAR` | 0 | 0 | 21969 | 0 | 4-8 | `99999.99` (18689); `9999.99` (2634); `999.99` (254) | não |
| `limite_cheque_especial` | `VARCHAR` | 0 | 0 | 21870 | 0 | 6-8 | `99999.99` (11406); `9999.99` (10043); `999.99` (551) | não |
| `status_conta` | `VARCHAR` | 0 | 0 | 3 | 0 | 5-9 | `AAAAA` (21538); `AAAAAAAAA` (462) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 46 | 0 | 25-26 | `9999-99-99 99:99:99.999999` (21500); `9999-99-99 99:99:99.99999` (500) | não |

## `raw.contratos_credito`

- Registros: **15000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `contrato_credito_id` | `VARCHAR` | 0 | 0 | 15000 | 0 | 1-5 | `9999` (9000); `99999` (5001); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 15000 | 0 | 1-5 | `9999` (9000); `99999` (5001); `999` (900) | sim |
| `conta_id` | `VARCHAR` | 0 | 0 | 15000 | 0 | 1-5 | `9999` (9000); `99999` (5001); `999` (900) | sim |
| `produto_credito_id` | `VARCHAR` | 0 | 0 | 8 | 0 | 3-3 | `999` (15000) | não |
| `numero_contrato` | `VARCHAR` | 0 | 0 | 15000 | 0 | 17-17 | `AAA-9999-99999999` (15000) | sim |
| `data_contratacao` | `VARCHAR` | 0 | 0 | 1250 | 0 | 10-10 | `9999-99-99` (15000) | não |
| `valor_contratado` | `VARCHAR` | 0 | 0 | 14984 | 0 | 7-9 | `99999.99` (12149); `9999.99` (1904); `999999.99` (947) | não |
| `taxa_juros_mensal` | `VARCHAR` | 0 | 0 | 8 | 0 | 6-6 | `9.9999` (15000) | não |
| `quantidade_parcelas` | `VARCHAR` | 0 | 0 | 6 | 0 | 2-2 | `99` (15000) | não |
| `valor_parcela` | `VARCHAR` | 0 | 0 | 14639 | 0 | 5-8 | `9999.99` (7712); `999.99` (6623); `99.99` (395) | não |
| `saldo_devedor` | `VARCHAR` | 0 | 0 | 14972 | 0 | 6-9 | `99999.99` (9318); `9999.99` (4949); `999999.99` (462) | não |
| `status_contrato` | `VARCHAR` | 0 | 0 | 4 | 0 | 5-12 | `AAAAA` (14388); `AAAAAAAAAAA` (249); `AAAAAAAAAAAA` (209) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 51 | 0 | 25-26 | `9999-99-99 99:99:99.99999` (14600); `9999-99-99 99:99:99.999999` (400) | não |

## `raw.cooperados`

- Registros: **20000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `cooperado_id` | `VARCHAR` | 0 | 0 | 20000 | 0 | 1-5 | `99999` (10001); `9999` (9000); `999` (900) | sim |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (12800); `9` (7200) | não |
| `codigo_cooperado` | `VARCHAR` | 0 | 0 | 20000 | 0 | 12-12 | `AAAA99999999` (20000) | sim |
| `nome_completo` | `VARCHAR` | 0 | 0 | 20000 | 0 | 25-37 | `AAAAAA AAAAAAAAA AAAA?AAA 99999` (2727); `AAAAAA AAAAAAAAA AAAA?AAA 9999` (2454); `AAAAA AAAAAAAAA AAAA?AAA 99999` (1818) | sim |
| `cpf` | `VARCHAR` | 0 | 0 | 20000 | 0 | 12-16 | `999999999-99` (18182); `99999999/9999-99` (1818) | sim |
| `tipo_pessoa` | `VARCHAR` | 0 | 0 | 2 | 0 | 2-2 | `AA` (20000) | não |
| `data_nascimento` | `VARCHAR` | 1818 | 0 | 16545 | 0 | 10-10 | `9999-99-99` (18182) | não |
| `sexo` | `VARCHAR` | 1818 | 0 | 2 | 0 | 8-9 | `AAAAAAAA` (9091); `AAAAAAAAA` (9091) | não |
| `estado_civil` | `VARCHAR` | 1818 | 0 | 4 | 0 | 6-13 | `AAAAAA` (4546); `AAAAAAAA` (4546); `AAA?A AAA?AAA` (4545) | não |
| `cidade` | `VARCHAR` | 0 | 0 | 10 | 0 | 6-22 | `AAAAAAAA` (4000); `AAA?AA` (2000); `AAA?AAA AA AAAAAAAAA` (2000) | não |
| `estado` | `VARCHAR` | 0 | 0 | 1 | 0 | 2-2 | `AA` (20000) | não |
| `renda_mensal` | `VARCHAR` | 0 | 0 | 19906 | 0 | 7-9 | `99999.99` (10345); `9999.99` (8635); `999999.99` (1020) | não |
| `profissao` | `VARCHAR` | 0 | 0 | 9 | 0 | 6-16 | `AAAAAAAAA` (4444); `AAAAAAAA AAAAA` (2223); `AAAAAAAAAAA` (2223) | não |
| `email` | `VARCHAR` | 0 | 0 | 20000 | 0 | 22-26 | `AAAAAAAAA99999?AAAAAAA.AAA` (10001); `AAAAAAAAA9999?AAAAAAA.AAA` (9000); `AAAAAAAAA999?AAAAAAA.AAA` (900) | sim |
| `telefone` | `VARCHAR` | 0 | 0 | 20000 | 0 | 11-11 | `99999999999` (20000) | sim |
| `data_associacao` | `VARCHAR` | 0 | 0 | 3300 | 0 | 10-10 | `9999-99-99` (20000) | não |
| `status_cooperado` | `VARCHAR` | 0 | 0 | 3 | 0 | 5-9 | `AAAAA` (19420); `AAAAAAA` (374); `AAAAAAAAA` (206) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 61 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (20000) | não |

## `raw.investimentos`

- Registros: **12000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `investimento_id` | `VARCHAR` | 0 | 0 | 12000 | 0 | 1-5 | `9999` (9000); `99999` (2001); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 12000 | 0 | 1-5 | `9999` (6334); `99999` (4667); `999` (900) | sim |
| `conta_id` | `VARCHAR` | 0 | 0 | 12000 | 0 | 1-5 | `9999` (6000); `99999` (5334); `999` (600) | sim |
| `codigo_aplicacao` | `VARCHAR` | 0 | 0 | 12000 | 0 | 12-12 | `AAA-99999999` (12000) | sim |
| `tipo_investimento` | `VARCHAR` | 0 | 0 | 6 | 0 | 3-18 | `AAA` (6000); `AAAAAAAA_AAAAAAAAA` (2000); `AAAAA_AAAAA_AAAA` (2000) | não |
| `data_aplicacao` | `VARCHAR` | 0 | 0 | 1300 | 0 | 10-10 | `9999-99-99` (12000) | não |
| `data_vencimento` | `VARCHAR` | 0 | 0 | 199 | 0 | 10-10 | `9999-99-99` (12000) | não |
| `valor_aplicado` | `VARCHAR` | 0 | 0 | 11994 | 0 | 6-9 | `99999.99` (7141); `999999.99` (4126); `9999.99` (701) | não |
| `valor_atual` | `VARCHAR` | 0 | 0 | 11996 | 0 | 6-9 | `99999.99` (6545); `999999.99` (4786); `9999.99` (643) | não |
| `rentabilidade_percentual` | `VARCHAR` | 0 | 0 | 11631 | 0 | 6-7 | `9.9999` (6595); `99.9999` (5405) | não |
| `status_investimento` | `VARCHAR` | 0 | 0 | 2 | 0 | 5-9 | `AAAAA` (11774); `AAAAAAAAA` (226) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 30 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (12000) | não |

## `raw.lancamentos_contabeis`

- Registros: **300000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `lancamento_id` | `VARCHAR` | 0 | 0 | 300000 | 0 | 1-6 | `999999` (200001); `99999` (90000); `9999` (9000) | sim |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (192000); `9` (108000) | não |
| `conta_id` | `VARCHAR` | 0 | 0 | 22000 | 0 | 1-5 | `99999` (160014); `9999` (126000); `999` (12600) | não |
| `data_lancamento` | `VARCHAR` | 0 | 0 | 86400 | 0 | 19-19 | `9999-99-99 99:99:99` (300000) | não |
| `codigo_historico` | `VARCHAR` | 0 | 0 | 10 | 0 | 6-10 | `AAA_AAA` (150000); `AAAA_AAA` (90000); `AAAAAA` (30000) | não |
| `descricao_historico` | `VARCHAR` | 0 | 0 | 10 | 0 | 11-25 | `AAA AAAAAAA` (60000); `A?AAAA AA AAAAAAA` (30000); `AAA AAAAAAAA` (30000) | não |
| `tipo_lancamento` | `VARCHAR` | 0 | 0 | 2 | 0 | 6-7 | `AAAAAA` (150000); `AAAAAAA` (150000) | não |
| `valor_lancamento` | `VARCHAR` | 0 | 0 | 282547 | 0 | 4-8 | `99999.99` (179816); `9999.99` (108123); `999.99` (10912) | não |
| `centro_custo` | `VARCHAR` | 0 | 0 | 25 | 0 | 12-12 | `AAAAAAA_9999` (300000) | não |
| `conta_contabil` | `VARCHAR` | 0 | 0 | 6 | 0 | 8-8 | `9.9.9.99` (300000) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 20 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (300000) | não |

