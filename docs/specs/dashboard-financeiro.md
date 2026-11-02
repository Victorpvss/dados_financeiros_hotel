# Spec: Dashboard Financeiro

## Objetivo

Apresentar uma visão explorável dos indicadores financeiros da cooperativa,
permitindo comparar resultados por estado e período sem alterar os dados do
banco. A interface é feita em Streamlit e consulta o DuckDB em modo somente
leitura.

## Usuários e necessidade

Analistas e avaliadores do projeto precisam identificar tendências de
investimentos, satisfação das agências e movimentação das contas, além de
inspecionar os marts em uma tela de exploração.

## Fontes de dados

- `refined.investimentos`: aplicações, valores aplicados/atuais, data e cooperado.
- `refined.cooperados`: estado de residência/vínculo do cooperado usado para
  filtrar investimentos.
- `refined.atendimentos_relacionamento`: nota e data do atendimento.
- `refined.agencias`: estado da agência usado para filtrar atendimentos e
  lançamentos.
- `refined.lancamentos_contabeis`: valor, data e conta dos lançamentos.
- Os marts existentes podem ser consultados para navegação e referência, mas as
  métricas do dashboard devem ser recalculadas na granularidade necessária para
  respeitar os filtros.

## Filtros globais

### Estado das agências

Opções: `Todos` e estados presentes nos dados de agências.

- Satisfação e movimentações são filtradas pelo estado da agência.
- Investimentos são filtrados pelo estado do cooperado associado ao
  investimento.
- `Todos` remove a restrição de estado.

### Período

Opções: todo o histórico, últimos 12 meses e últimos 6 meses.

- O limite final é o mês mais recente existente nos dados relevantes.
- Para investimentos, o período usa `data_aplicacao`.
- Para satisfação, usa `data_abertura` do atendimento.
- Para movimentações, usa `data_lancamento`.
- O limite inicial inclui o mês mais antigo do intervalo selecionado.
- `Todo o histórico` não aplica limite de data.

## Indicadores e semântica

- **Aplicado:** soma de `valor_aplicado` nos investimentos filtrados por estado
  do cooperado e período de aplicação.
- **Carteira atual:** soma de `valor_atual` desses mesmos investimentos. É uma
  fotografia atual dos investimentos originados no recorte, não um saldo
  histórico na data final do filtro.
- **Variação da carteira:** percentual entre o valor atual e o valor aplicado
  no recorte.
- **Satisfação:** média das notas não nulas dos atendimentos filtrados por
  estado da agência e período de abertura.
- **Movimentação:** soma dos valores dos lançamentos filtrados por estado da
  agência e período do lançamento. A quantidade de lançamentos deve usar o
  mesmo recorte.

## Visualizações

- Série mensal de quantidade de aplicações e média móvel de três meses.
- Série mensal de valores aplicados e média móvel de três meses.
- Satisfação média por agência no recorte.
- Valor aplicado por tipo de investimento no recorte.
- Contas com maior valor movimentado no recorte, ordenadas do maior para o
  menor; empates são resolvidos por quantidade de lançamentos e identificador
  da conta.
- O explorador de dados continua disponível como navegação secundária.

## Requisitos não funcionais

- Consultas de interface usam conexão DuckDB somente leitura.
- Valores financeiros são exibidos em reais; os cartões podem abreviar valores
  em milhões, desde que a unidade esteja visível.
- Layout deve permanecer legível em desktop e celular.
- Os dados do projeto são sintéticos; o dashboard não deve sugerir que são
  transações reais.

## Estados e erros

- Se os marts/refined necessários estiverem ausentes ou vazios, exibir uma
  mensagem útil em vez de uma exceção sem contexto.
- Se a combinação de filtros não retornar dados, indicar ausência de dados no
  recorte; não exibir gráficos enganosos como se os valores fossem zero.
- Falhas de conexão ou SQL devem ser apresentadas sem expor credenciais.

## Critérios de aceite

1. As opções de período incluem todo o histórico, últimos 12 meses e últimos 6
   meses.
2. Alterar estado ou período recalcula todos os KPIs e gráficos compatíveis com
   a semântica definida nesta spec.
3. O filtro de estado oferece todos os estados presentes em `refined.agencias`.
4. O ranking de movimentação é decrescente e estável para empates.
5. Os dados permanecem inalterados ao navegar pelo dashboard.
6. A tela principal e o explorador continuam utilizáveis em desktop e celular.