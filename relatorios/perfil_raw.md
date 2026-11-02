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
| `status_agencia` | `VARCHAR` | 0 | 0 | 3 | 0 | 5-10 | `AAAAA` (22); `AA_AAAAAAA` (2); `AAAAAAA` (1) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 25 | 0 | 10-10 | `9999-99-99` (25) | sim |
| `update_date` | `VARCHAR` | 0 | 0 | 25 | 0 | 19-19 | `9999-99-99 99:99:99` (25) | sim |

## `raw.atendimentos_relacionamento`

- Registros: **60000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `atendimento_id` | `VARCHAR` | 0 | 0 | 60000 | 0 | 1-5 | `99999` (50001); `9999` (9000); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 19034 | 0 | 1-5 | `99999` (30089); `9999` (26918); `999` (2719) | não |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (38652); `9` (21348) | não |
| `canal_atendimento` | `VARCHAR` | 0 | 0 | 5 | 0 | 3-16 | `AAAAAAAA` (25516); `AAA` (16293); `AAAAAAAAAA` (10899) | não |
| `motivo_atendimento` | `VARCHAR` | 0 | 0 | 12 | 0 | 3-21 | `AAAAAAAAAA` (9925); `AAA` (5091); `AAAAAAAA` (5061) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 59986 | 0 | 19-19 | `9999-99-99 99:99:99` (60000) | não |
| `data_encerramento` | `VARCHAR` | 3632 | 0 | 56368 | 0 | 26-26 | `9999-99-99 99:99:99.999999` (56368) | não |
| `status_atendimento` | `VARCHAR` | 0 | 0 | 3 | 0 | 9-12 | `AAAAAAAAA` (56368); `AA_AAAAAAAAA` (3632) | não |
| `nota_satisfacao` | `VARCHAR` | 3632 | 0 | 10 | 0 | 1-2 | `9` (42694); `99` (13674) | não |
| `descricao_resumida` | `VARCHAR` | 0 | 0 | 60000 | 0 | 66-100 | `AAAAAAAAAAA AA AAAAAAAAAA AAAAAAAA AAAA AAAAA AAAAAAAA. AAAAAAAAA AAAAAAAA 99999.` (3524); `AAAAAAAAAAA AA AAAAAAAAAA AAAAAAAA AAAA AAAAA AAA. AAAAAAAAA AAAAAAAA 99999.` (2225); `AAAAAAAAAAA AA AAA AAAAAAAA AAAA AAAAA AAAAAAAA. AAAAAAAAA AAAAAAAA 99999.` (1850) | sim |
| `update_date` | `VARCHAR` | 0 | 0 | 59968 | 0 | 19-19 | `9999-99-99 99:99:99` (60000) | não |

## `raw.contas_correntes`

- Registros: **22000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `conta_id` | `VARCHAR` | 0 | 0 | 22000 | 0 | 1-5 | `99999` (12001); `9999` (9000); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 20000 | 0 | 1-5 | `99999` (10975); `9999` (9928); `999` (991) | não |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (14140); `9` (7860) | não |
| `numero_conta` | `VARCHAR` | 0 | 0 | 22000 | 0 | 13-13 | `9999-99999999` (22000) | sim |
| `tipo_conta` | `VARCHAR` | 0 | 0 | 5 | 0 | 13-17 | `AAAAA_AAAAAAAA_AA` (8798); `AAAAA_AAAAAAAA` (6615); `AAAAA_AAAAAAA` (6587) | não |
| `data_abertura` | `VARCHAR` | 0 | 0 | 5309 | 0 | 10-10 | `9999-99-99` (22000) | não |
| `saldo_atual` | `VARCHAR` | 0 | 0 | 21866 | 0 | 5-9 | `9999.99` (9752); `99999.99` (8423); `999.99` (1098) | não |
| `limite_cheque_especial` | `VARCHAR` | 0 | 0 | 21287 | 0 | 6-8 | `9999.99` (15787); `99999.99` (5031); `999.99` (1182) | não |
| `status_conta` | `VARCHAR` | 0 | 0 | 3 | 0 | 5-9 | `AAAAA` (20679); `AAAAAAA` (870); `AAAAAAAAA` (451) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 21998 | 0 | 19-19 | `9999-99-99 99:99:99` (22000) | não |

## `raw.contratos_credito`

- Registros: **15000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `contrato_credito_id` | `VARCHAR` | 0 | 0 | 15000 | 0 | 1-5 | `9999` (9000); `99999` (5001); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 10299 | 0 | 1-5 | `99999` (7464); `9999` (6789); `999` (669) | não |
| `conta_id` | `VARCHAR` | 0 | 0 | 10799 | 0 | 1-5 | `99999` (8282); `9999` (5957); `999` (691) | não |
| `produto_credito_id` | `VARCHAR` | 0 | 0 | 8 | 0 | 3-3 | `999` (15000) | não |
| `numero_contrato` | `VARCHAR` | 0 | 0 | 15000 | 0 | 17-18 | `AAA-9999-99999999` (9999); `AAA-99999-99999999` (5001) | sim |
| `data_contratacao` | `VARCHAR` | 0 | 0 | 3202 | 0 | 10-10 | `9999-99-99` (15000) | não |
| `valor_contratado` | `VARCHAR` | 0 | 0 | 14957 | 0 | 7-9 | `99999.99` (11955); `999999.99` (1589); `9999.99` (1456) | não |
| `taxa_juros_mensal` | `VARCHAR` | 0 | 0 | 11239 | 0 | 6-6 | `9.9999` (15000) | não |
| `quantidade_parcelas` | `VARCHAR` | 0 | 0 | 8 | 0 | 1-2 | `99` (13085); `9` (1915) | não |
| `valor_parcela` | `VARCHAR` | 0 | 0 | 14756 | 0 | 5-8 | `9999.99` (9222); `999.99` (4855); `99999.99` (873) | não |
| `saldo_devedor` | `VARCHAR` | 0 | 0 | 4494 | 0 | 4-9 | `9.99` (10504); `99999.99` (2609); `9999.99` (1494) | não |
| `status_contrato` | `VARCHAR` | 0 | 0 | 4 | 0 | 5-9 | `AAAAA` (10512); `AAAAAAA` (3003); `AA_AAAAAA` (1168) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 14998 | 0 | 19-19 | `9999-99-99 99:99:99` (15000) | não |

## `raw.cooperados`

- Registros: **20000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `cooperado_id` | `VARCHAR` | 0 | 0 | 20000 | 0 | 1-5 | `99999` (10001); `9999` (9000); `999` (900) | sim |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (12846); `9` (7154) | não |
| `codigo_cooperado` | `VARCHAR` | 0 | 0 | 20000 | 0 | 12-12 | `AAAA99999999` (20000) | sim |
| `nome_completo` | `VARCHAR` | 0 | 0 | 10777 | 0 | 13-28 | `AAAAAA AAAAAAA AAAAAAA` (647); `AAAAAA AAAAAAA AAAAA` (535); `AAAAAA AAAAAAA AAAAAA` (515) | não |
| `cpf` | `VARCHAR` | 0 | 0 | 20000 | 0 | 12-16 | `999999999-99` (18182); `99999999/9999-99` (1818) | sim |
| `tipo_pessoa` | `VARCHAR` | 0 | 0 | 2 | 0 | 2-2 | `AA` (20000) | não |
| `data_nascimento` | `VARCHAR` | 1818 | 0 | 12580 | 0 | 10-10 | `9999-99-99` (18182) | não |
| `sexo` | `VARCHAR` | 1818 | 0 | 2 | 0 | 8-9 | `AAAAAAAAA` (9186); `AAAAAAAA` (8996) | não |
| `estado_civil` | `VARCHAR` | 1818 | 0 | 5 | 0 | 5-13 | `AAAAAAAA` (3716); `AAAAA AAAAAAA` (3665); `AAAAAAAAAA` (3648) | não |
| `cidade` | `VARCHAR` | 0 | 0 | 10 | 0 | 6-22 | `AAAAAAAA` (3998); `AAAAA AA AAAAAAA` (2491); `AAAAA AAA?AAA AA AAAAA` (2402) | não |
| `estado` | `VARCHAR` | 0 | 0 | 1 | 0 | 2-2 | `AA` (20000) | não |
| `renda_mensal` | `VARCHAR` | 0 | 0 | 19455 | 0 | 7-9 | `9999.99` (15013); `99999.99` (4852); `999999.99` (135) | não |
| `profissao` | `VARCHAR` | 0 | 0 | 14 | 0 | 7-17 | `AAAAAAAAAA` (5698); `AAAAAAAA` (4222); `AAAAAAAAA` (2938) | não |
| `email` | `VARCHAR` | 0 | 0 | 20000 | 0 | 22-26 | `AAAAAAAAA99999?AAAAAAA.AAA` (10001); `AAAAAAAAA9999?AAAAAAA.AAA` (9000); `AAAAAAAAA999?AAAAAAA.AAA` (900) | sim |
| `telefone` | `VARCHAR` | 0 | 0 | 20000 | 0 | 11-11 | `99999999999` (20000) | sim |
| `data_associacao` | `VARCHAR` | 0 | 0 | 5893 | 0 | 10-10 | `9999-99-99` (20000) | não |
| `status_cooperado` | `VARCHAR` | 0 | 0 | 3 | 0 | 5-8 | `AAAAA` (18614); `AAAAAAA` (1000); `AAAAAAAA` (386) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 19996 | 0 | 19-19 | `9999-99-99 99:99:99` (20000) | não |

## `raw.investimentos`

- Registros: **12000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `investimento_id` | `VARCHAR` | 0 | 0 | 12000 | 0 | 1-5 | `9999` (9000); `99999` (2001); `999` (900) | sim |
| `cooperado_id` | `VARCHAR` | 0 | 0 | 8926 | 0 | 1-5 | `99999` (6038); `9999` (5402); `999` (512) | não |
| `conta_id` | `VARCHAR` | 0 | 0 | 9281 | 0 | 1-5 | `99999` (6567); `9999` (4876); `999` (497) | não |
| `codigo_aplicacao` | `VARCHAR` | 0 | 0 | 12000 | 0 | 12-12 | `AAA-99999999` (12000) | sim |
| `tipo_investimento` | `VARCHAR` | 0 | 0 | 6 | 0 | 3-18 | `AAA` (9142); `AAAAA_AAAAA_AAAA` (1663); `AAAAAAAA_AAAAAAAAA` (1195) | não |
| `data_aplicacao` | `VARCHAR` | 0 | 0 | 2432 | 0 | 10-10 | `9999-99-99` (12000) | não |
| `data_vencimento` | `VARCHAR` | 0 | 0 | 3541 | 0 | 10-10 | `9999-99-99` (12000) | não |
| `valor_aplicado` | `VARCHAR` | 0 | 0 | 11968 | 0 | 6-9 | `99999.99` (7438); `9999.99` (3671); `999999.99` (825) | não |
| `valor_atual` | `VARCHAR` | 0 | 0 | 11985 | 0 | 6-9 | `99999.99` (7715); `9999.99` (3233); `999999.99` (1007) | não |
| `rentabilidade_percentual` | `VARCHAR` | 0 | 0 | 11430 | 0 | 6-7 | `9.9999` (6403); `99.9999` (5597) | não |
| `status_investimento` | `VARCHAR` | 0 | 0 | 2 | 0 | 5-9 | `AAAAAAAAA` (8239); `AAAAA` (3761) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 11999 | 0 | 19-19 | `9999-99-99 99:99:99` (12000) | não |

## `raw.lancamentos_contabeis`

- Registros: **300000**
- Linhas duplicadas exatas: **0**

| Coluna | Tipo atual | Nulos | Vazios | Distintos | Espaços nas bordas | Tamanho (min-max) | Formatos mascarados mais comuns | Único observado |
|---|---:|---:|---:|---:|---:|---:|---|:---:|
| `lancamento_id` | `VARCHAR` | 0 | 0 | 300000 | 0 | 1-6 | `999999` (200001); `99999` (90000); `9999` (9000) | sim |
| `agencia_id` | `VARCHAR` | 0 | 0 | 25 | 0 | 1-2 | `99` (192726); `9` (107274) | não |
| `conta_id` | `VARCHAR` | 0 | 0 | 22000 | 0 | 1-5 | `99999` (163883); `9999` (122555); `999` (12268) | não |
| `data_lancamento` | `VARCHAR` | 0 | 0 | 299625 | 0 | 19-19 | `9999-99-99 99:99:99` (300000) | não |
| `codigo_historico` | `VARCHAR` | 0 | 0 | 12 | 0 | 5-13 | `AAA_AAA` (141105); `AAAA_AAA` (35683); `AAA_AAAAAA` (32941) | não |
| `descricao_historico` | `VARCHAR` | 0 | 0 | 12 | 0 | 11-22 | `AAA AAAAAAA` (53996); `AAA AAAAAAAA` (51031); `AAAAAAAAA AA AAAAAA` (32941) | não |
| `tipo_lancamento` | `VARCHAR` | 0 | 0 | 2 | 0 | 6-7 | `AAAAAA` (179914); `AAAAAAA` (120086) | não |
| `valor_lancamento` | `VARCHAR` | 0 | 0 | 151489 | 0 | 4-9 | `999.99` (160053); `9999.99` (74535); `99.99` (54398) | não |
| `centro_custo` | `VARCHAR` | 0 | 0 | 25 | 0 | 12-12 | `AAAAAAA_9999` (300000) | não |
| `conta_contabil` | `VARCHAR` | 0 | 0 | 6 | 0 | 8-8 | `9.9.9.99` (300000) | não |
| `update_date` | `VARCHAR` | 0 | 0 | 299304 | 0 | 19-19 | `9999-99-99 99:99:99` (300000) | não |

