import calendar
import csv
import math
import random
import shutil
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
PASTA_FONTE = RAIZ_PROJETO / "fonte_dados"
PASTA_RAW = RAIZ_PROJETO / "raw"
SEMENTE = 20261102

ARQUIVOS = (
    "agencias.csv",
    "cooperados.csv",
    "contas_correntes.csv",
    "contratos_credito.csv",
    "atendimentos_relacionamento.csv",
    "investimentos.csv",
    "lancamentos_contabeis.csv",
)

PRIMEIROS_NOMES = (
    "Ana", "Beatriz", "Bruno", "Caio", "Camila", "Carla", "Daniel",
    "Eduardo", "Elaine", "Felipe", "Fernanda", "Gabriel", "Helena",
    "Igor", "Isabela", "Joao", "Julia", "Larissa", "Lucas", "Mariana",
    "Marcos", "Mateus", "Paula", "Rafael", "Renata", "Sofia", "Thiago",
    "Victor", "Yasmin", "Andre", "Bianca", "Diego", "Luana", "Pedro",
)
NOMES_MEIO = (
    "Almeida", "Andrade", "Barbosa", "Carvalho", "Costa", "Dias", "Freitas",
    "Lima", "Mendes", "Oliveira", "Pereira", "Ribeiro", "Rocha", "Santos",
    "Silva", "Souza", "Teixeira", "Vieira", "Araujo", "Cardoso", "Nunes",
)
SOBRENOMES = (
    "Almeida", "Barbosa", "Carvalho", "Costa", "Fernandes", "Lima", "Mendes",
    "Monteiro", "Oliveira", "Pereira", "Ribeiro", "Rocha", "Santos", "Silva",
    "Souza", "Teixeira", "Vieira", "Araujo", "Cardoso", "Nascimento",
)
PROFISSOES = (
    "Agricultor", "Autonomo", "Comerciante", "Engenheiro", "Enfermeiro",
    "Microempreendedor", "Professor", "Servidor Publico", "Motorista",
    "Produtor Rural", "Analista", "Aposentado", "Tecnico", "Advogado",
)
ESTADOS_CIVIS = ("Solteiro", "Casado", "Divorciado", "Uniao Estavel", "Viuvo")
LOCALIDADES_POR_ESTADO = {
    "BA": (
        "Nordeste",
        (
            "Salvador",
            "Feira de Santana",
            "Vitoria da Conquista",
            "Ilheus",
            "Juazeiro",
        ),
    ),
    "PE": (
        "Nordeste",
        (
            "Recife",
            "Caruaru",
            "Petrolina",
            "Olinda",
            "Garanhuns",
        ),
    ),
    "MG": (
        "Sudeste",
        (
            "Belo Horizonte",
            "Uberlandia",
            "Juiz de Fora",
            "Montes Claros",
            "Pouso Alegre",
        ),
    ),
    "RJ": (
        "Sudeste",
        (
            "Rio de Janeiro",
            "Niteroi",
            "Petropolis",
            "Volta Redonda",
            "Campos dos Goytacazes",
        ),
    ),
    "SP": (
        "Sudeste",
        (
            "Sao Paulo",
            "Campinas",
            "Santos",
            "Ribeirao Preto",
            "Sao Jose dos Campos",
        ),
    ),
}
TIPOS_CONTA_PF = ("conta_corrente_pf", "conta_poupanca", "conta_salario")
TIPOS_CONTA_PJ = ("conta_corrente_pj", "conta_poupanca_pj")
MOTIVOS = (
    "duvida_conta_corrente", "solicitacao_cartao", "capital_giro",
    "investimentos", "pix", "cadastro", "reclamacao", "emprestimo",
    "renegociacao", "acesso_digital", "seguro", "tarifas",
)
CANAIS = ("app", "internet_banking", "presencial", "telefone", "whatsapp")
CODIGOS_LANCAMENTO = (
    ("PIX_ENV", "Pix enviado", "debito"),
    ("PIX_REC", "Pix recebido", "credito"),
    ("PAG_BOLETO", "Pagamento de boleto", "debito"),
    ("TED_ENV", "Transferencia enviada", "debito"),
    ("TED_REC", "Transferencia recebida", "credito"),
    ("TARIFA", "Cobranca de tarifa", "debito"),
    ("CRED_LIB", "Liberacao de credito", "credito"),
    ("PARC_DEB", "Debito de parcela", "debito"),
    ("DEPOSITO", "Deposito em conta", "credito"),
    ("SAQUE", "Saque em terminal", "debito"),
    ("RENDIMENTO", "Credito de rendimento", "credito"),
    ("COMPRA_CARTAO", "Compra no cartao", "debito"),
)


def sortear_data(
    gerador: random.Random,
    inicio: date,
    fim: date,
) -> date:
    dias = (fim - inicio).days
    return inicio + timedelta(days=gerador.randint(0, dias))


def construir_pesos_meses_investimento(
    gerador: random.Random,
) -> tuple[list[tuple[int, int]], list[float]]:
    meses = []
    pesos = []
    indice = 0
    ano, mes = 2020, 1
    sazonalidade = (0.78, 0.82, 0.95, 1.0, 1.08, 1.02, 0.92, 1.05, 0.96, 1.12, 1.35, 1.55)
    while (ano, mes) <= (2026, 10):
        progresso = indice / 81
        tendencia = 0.75 + 0.5 * progresso
        campanha = gerador.uniform(0.65, 1.4)
        meses.append((ano, mes))
        pesos.append(tendencia * sazonalidade[mes - 1] * campanha)
        indice += 1
        if mes == 12:
            ano += 1
            mes = 1
        else:
            mes += 1

    return meses, pesos


def sortear_mes_investimento(
    gerador: random.Random,
    meses: list[tuple[int, int]],
    pesos: list[float],
) -> date:
    ano, mes = gerador.choices(meses, weights=pesos, k=1)[0]
    dia = gerador.randint(1, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


def sortear_timestamp(
    gerador: random.Random,
    inicio: datetime,
    fim: datetime,
) -> datetime:
    segundos = int((fim - inicio).total_seconds())
    return inicio + timedelta(seconds=gerador.randint(0, segundos))


def dinheiro(valor: float) -> str:
    return f"{valor:.2f}"


def valor_log_normal(
    gerador: random.Random,
    mediana: float,
    dispersao: float,
    minimo: float,
    maximo: float,
) -> float:
    return min(max(gerador.lognormvariate(math.log(mediana), dispersao), minimo), maximo)


def ler_csv(caminho: Path) -> tuple[list[str], list[dict[str, str]]]:
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor.fieldnames or []), list(leitor)


def gravar_csv(caminho: Path, colunas: list[str], linhas: list[dict[str, str]]) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=colunas,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        escritor.writeheader()
        escritor.writerows(linhas)


def gerar_dados_sinteticos(
    pasta_fonte: Path = PASTA_FONTE,
    pasta_raw: Path = PASTA_RAW,
    semente: int = SEMENTE,
) -> dict[str, int]:
    gerador = random.Random(semente)
    colunas_por_arquivo = {}
    dados = {}
    for arquivo in ARQUIVOS:
        colunas, linhas = ler_csv(pasta_fonte / arquivo)
        colunas_por_arquivo[arquivo] = colunas
        dados[arquivo] = linhas

    agencias = dados["agencias.csv"]
    agora_inicio = datetime(2025, 1, 1)
    agora_fim = datetime(2026, 10, 31, 23, 59, 59)

    estados_agencias = [
        estado
        for estado in LOCALIDADES_POR_ESTADO
        for _ in range(len(agencias) // len(LOCALIDADES_POR_ESTADO))
    ]
    estados_agencias.extend(
        gerador.choices(
            list(LOCALIDADES_POR_ESTADO),
            k=len(agencias) - len(estados_agencias),
        )
    )
    gerador.shuffle(estados_agencias)
    indice_cidade_por_estado = dict.fromkeys(LOCALIDADES_POR_ESTADO, 0)

    for agencia, estado in zip(agencias, estados_agencias, strict=True):
        regiao, cidades = LOCALIDADES_POR_ESTADO[estado]
        indice_cidade = indice_cidade_por_estado[estado]
        agencia["estado"] = estado
        agencia["regiao"] = regiao
        agencia["cidade"] = cidades[indice_cidade % len(cidades)]
        indice_cidade_por_estado[estado] += 1
        agencia["data_abertura"] = sortear_data(
            gerador, date(2001, 1, 1), date(2022, 12, 31)
        ).isoformat()
        agencia["status_agencia"] = gerador.choices(
            ["ativa", "em_reforma", "inativa"], [0.94, 0.04, 0.02]
        )[0]
        agencia["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

    cooperados = dados["cooperados.csv"]
    tipo_por_cooperado = {}
    agencia_por_cooperado = {}
    for cooperado in cooperados:
        cooperado_id = int(cooperado["cooperado_id"])
        tipo_pessoa = cooperado["tipo_pessoa"]
        tipo_por_cooperado[cooperado["cooperado_id"]] = tipo_pessoa
        agencia = gerador.choice(agencias)
        cooperado["agencia_id"] = agencia["agencia_id"]
        agencia_por_cooperado[cooperado["cooperado_id"]] = agencia["agencia_id"]
        cooperado["cidade"] = agencia["cidade"]
        cooperado["estado"] = agencia["estado"]
        cooperado["estado_civil"] = gerador.choice(ESTADOS_CIVIS)
        cooperado["profissao"] = gerador.choice(PROFISSOES)
        cooperado["status_cooperado"] = gerador.choices(
            ["ativo", "inativo", "suspenso"], [0.93, 0.05, 0.02]
        )[0]
        cooperado["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

        cooperado["nome_completo"] = " ".join(
            [
                gerador.choice(PRIMEIROS_NOMES),
                gerador.choice(NOMES_MEIO),
                gerador.choice(SOBRENOMES),
            ]
        )
        cooperado["email"] = f"cooperado{cooperado_id}@example.com"
        cooperado["sexo"] = gerador.choice(["Feminino", "Masculino"])

        if tipo_pessoa == "PF":
            nascimento = sortear_data(
                gerador, date(1945, 1, 1), date(2007, 12, 31)
            )
            cooperado["data_nascimento"] = nascimento.isoformat()
            cooperado["renda_mensal"] = dinheiro(
                valor_log_normal(gerador, 5200, 0.75, 1100, 85000)
            )
        else:
            cooperado["data_nascimento"] = ""
            cooperado["sexo"] = ""
            cooperado["estado_civil"] = ""
            cooperado["renda_mensal"] = dinheiro(
                valor_log_normal(gerador, 28000, 0.9, 5000, 500000)
            )
        cooperado["data_associacao"] = sortear_data(
            gerador, date(2010, 1, 1), date(2026, 10, 31)
        ).isoformat()

    contas = dados["contas_correntes.csv"]
    ids_cooperados = [cooperado["cooperado_id"] for cooperado in cooperados]
    atribuicoes = ids_cooperados.copy()
    atribuicoes.extend(gerador.choices(ids_cooperados, k=len(contas) - len(ids_cooperados)))
    gerador.shuffle(atribuicoes)
    conta_por_id = {}
    cooperado_por_conta = {}
    for conta, cooperado_id in zip(contas, atribuicoes, strict=True):
        conta_id = conta["conta_id"]
        cooperado = cooperados[int(cooperado_id) - 1]
        agencia_id = agencia_por_cooperado[cooperado_id]
        tipo_pessoa = tipo_por_cooperado[cooperado_id]
        conta["cooperado_id"] = cooperado_id
        conta["agencia_id"] = agencia_id
        conta["tipo_conta"] = gerador.choice(
            TIPOS_CONTA_PF if tipo_pessoa == "PF" else TIPOS_CONTA_PJ
        )
        conta["numero_conta"] = (
            f"{int(agencia_id):04d}-{int(conta_id):08d}"
        )
        data_abertura = sortear_data(
            gerador, date(2012, 1, 1), date(2026, 10, 31)
        )
        conta["data_abertura"] = data_abertura.isoformat()
        saldo = valor_log_normal(gerador, 8500, 1.35, 40, 350000)
        if gerador.random() < 0.09:
            saldo = -valor_log_normal(gerador, 900, 1.0, 20, 18000)
        conta["saldo_atual"] = dinheiro(saldo)
        renda = float(cooperado["renda_mensal"])
        conta["limite_cheque_especial"] = dinheiro(
            min(valor_log_normal(gerador, renda * 0.8, 0.55, 300, 50000), 50000)
        )
        conta["status_conta"] = gerador.choices(
            ["ativa", "inativa", "encerrada"], [0.94, 0.04, 0.02]
        )[0]
        conta["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")
        conta_por_id[conta_id] = conta
        cooperado_por_conta[conta_id] = cooperado_id

    contratos = dados["contratos_credito.csv"]
    for contrato in contratos:
        conta = gerador.choice(contas)
        contrato_id = int(contrato["contrato_credito_id"])
        contrato["conta_id"] = conta["conta_id"]
        contrato["cooperado_id"] = conta["cooperado_id"]
        contrato["produto_credito_id"] = str(gerador.choice(range(201, 209)))
        contrato["numero_contrato"] = f"CTR-{contrato_id:04d}-{gerador.randrange(10**8):08d}"
        data_contratacao = sortear_data(
            gerador, date(2018, 1, 1), date(2026, 10, 31)
        )
        contrato["data_contratacao"] = data_contratacao.isoformat()
        principal = valor_log_normal(gerador, 32000, 0.9, 1500, 450000)
        quantidade = gerador.choice([6, 12, 18, 24, 36, 48, 60, 72])
        taxa = gerador.uniform(0.007, 0.032)
        parcela = principal * taxa / (1 - (1 + taxa) ** -quantidade)
        status = gerador.choices(
            ["ativo", "quitado", "em_atraso", "cancelado"],
            [0.70, 0.20, 0.08, 0.02],
        )[0]
        meses_decorridos = max(
            0,
            (date(2026, 11, 1).year - data_contratacao.year) * 12
            + date(2026, 11, 1).month - data_contratacao.month,
        )
        parcelas_pagas = min(meses_decorridos, quantidade)
        restante = max(0, quantidade - parcelas_pagas)
        saldo_devedor = (
            0
            if status in {"quitado", "cancelado"}
            else min(principal, parcela * restante)
        )
        if status == "em_atraso":
            saldo_devedor = min(principal, saldo_devedor + parcela * gerador.randint(1, 3))
        contrato["valor_contratado"] = dinheiro(principal)
        contrato["taxa_juros_mensal"] = f"{taxa * 100:.4f}"
        contrato["quantidade_parcelas"] = str(quantidade)
        contrato["valor_parcela"] = dinheiro(parcela)
        contrato["saldo_devedor"] = dinheiro(saldo_devedor)
        contrato["status_contrato"] = status
        contrato["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

    atendimentos = dados["atendimentos_relacionamento.csv"]
    ids_notas = list(range(1, 11))
    pesos_notas = [1, 1, 2, 3, 5, 8, 12, 19, 25, 24]
    for atendimento in atendimentos:
        cooperado_id = gerador.choice(cooperados)["cooperado_id"]
        atendimento["cooperado_id"] = cooperado_id
        atendimento["agencia_id"] = agencia_por_cooperado[cooperado_id]
        atendimento["canal_atendimento"] = gerador.choices(
            CANAIS, [0.27, 0.12, 0.18, 0.19, 0.24]
        )[0]
        motivo = gerador.choice(MOTIVOS)
        atendimento["motivo_atendimento"] = motivo
        abertura = sortear_timestamp(
            gerador,
            datetime(2023, 1, 1, 7),
            datetime(2026, 10, 31, 21),
        )
        atendimento["data_abertura"] = abertura.isoformat(sep=" ")
        status = gerador.choices(
            ["encerrado", "em_andamento", "cancelado"], [0.91, 0.06, 0.03]
        )[0]
        atendimento["status_atendimento"] = status
        if status == "em_andamento":
            atendimento["data_encerramento"] = ""
            atendimento["nota_satisfacao"] = ""
        else:
            duracao = timedelta(minutes=gerador.triangular(4, 180, 32))
            atendimento["data_encerramento"] = (
                abertura + duracao
            ).isoformat(sep=" ")
            atendimento["nota_satisfacao"] = str(
                gerador.choices(ids_notas, pesos_notas)[0]
            )
        atendimento["descricao_resumida"] = (
            f"Solicitacao de {motivo.replace('_', ' ')} atendida pelo canal "
            f"{atendimento['canal_atendimento'].replace('_', ' ')}. "
            f"Protocolo ficticio {atendimento['atendimento_id']}."
        )
        atendimento["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

    investimentos = dados["investimentos.csv"]
    meses_investimento, pesos_meses_investimento = (
        construir_pesos_meses_investimento(gerador)
    )
    for investimento in investimentos:
        conta = gerador.choice(contas)
        investimento["conta_id"] = conta["conta_id"]
        investimento["cooperado_id"] = conta["cooperado_id"]
        investimento_id = int(investimento["investimento_id"])
        investimento["codigo_aplicacao"] = f"APL-{investimento_id:08d}"
        investimento["tipo_investimento"] = gerador.choices(
            ["cdb", "lca", "lci", "rdc", "fundo_renda_fixa", "poupanca_cooperada"],
            [0.24, 0.18, 0.16, 0.18, 0.14, 0.10],
        )[0]
        aplicacao = sortear_mes_investimento(
            gerador, meses_investimento, pesos_meses_investimento
        )
        prazo_dias = gerador.choice([90, 180, 365, 540, 720, 1080, 1825])
        vencimento = aplicacao + timedelta(days=prazo_dias)
        investimento["data_aplicacao"] = aplicacao.isoformat()
        investimento["data_vencimento"] = vencimento.isoformat()
        principal = valor_log_normal(gerador, 18000, 1.15, 500, 700000)
        rentabilidade_anual = gerador.uniform(0.035, 0.155)
        dias_aplicados = max(0, min((date(2026, 11, 1) - aplicacao).days, prazo_dias))
        valor_atual = principal * (1 + rentabilidade_anual) ** (dias_aplicados / 365)
        investimento["valor_aplicado"] = dinheiro(principal)
        investimento["valor_atual"] = dinheiro(valor_atual)
        investimento["rentabilidade_percentual"] = f"{rentabilidade_anual * 100:.4f}"
        investimento["status_investimento"] = (
            "resgatado" if vencimento < date(2026, 11, 1) else "ativo"
        )
        investimento["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

    lancamentos = dados["lancamentos_contabeis.csv"]
    for lancamento in lancamentos:
        conta = gerador.choice(contas)
        lancamento["conta_id"] = conta["conta_id"]
        lancamento["agencia_id"] = conta["agencia_id"]
        codigo, descricao, tipo = gerador.choices(
            CODIGOS_LANCAMENTO,
            [0.18, 0.17, 0.11, 0.06, 0.06, 0.08, 0.04, 0.08, 0.08, 0.05, 0.05, 0.04],
        )[0]
        lancamento["codigo_historico"] = codigo
        lancamento["descricao_historico"] = descricao
        lancamento["tipo_lancamento"] = tipo
        evento = sortear_timestamp(
            gerador,
            datetime(2023, 1, 1),
            datetime(2026, 10, 31, 23, 59, 59),
        )
        lancamento["data_lancamento"] = evento.isoformat(sep=" ")
        valor = valor_log_normal(gerador, 280, 1.35, 2, 120000)
        if codigo in {"CRED_LIB", "TED_ENV", "TED_REC"}:
            valor = valor_log_normal(gerador, 3200, 1.2, 50, 180000)
        lancamento["valor_lancamento"] = dinheiro(valor)
        lancamento["centro_custo"] = f"agencia_{int(conta['agencia_id']):04d}"
        lancamento["conta_contabil"] = gerador.choice(
            ["1.1.1.01", "1.1.1.02", "1.1.2.01", "2.1.1.01", "2.1.1.02", "3.1.1.01"]
        )
        lancamento["update_date"] = sortear_timestamp(
            gerador, agora_inicio, agora_fim
        ).isoformat(sep=" ")

    pasta_fonte.mkdir(parents=True, exist_ok=True)
    pasta_raw.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dados_sinteticos_") as temporario:
        pasta_temporaria = Path(temporario)
        for arquivo in ARQUIVOS:
            gravar_csv(
                pasta_temporaria / arquivo,
                colunas_por_arquivo[arquivo],
                dados[arquivo],
            )
        for arquivo in ARQUIVOS:
            shutil.copy2(pasta_temporaria / arquivo, pasta_fonte / arquivo)
            shutil.copy2(pasta_temporaria / arquivo, pasta_raw / arquivo)

    return {arquivo: len(dados[arquivo]) for arquivo in ARQUIVOS}


def main() -> None:
    totais = gerar_dados_sinteticos()
    print(f"Dados ficticios atualizados com semente {SEMENTE}.")
    for arquivo, quantidade in totais.items():
        print(f"{arquivo:<38} {quantidade:>8} registros")
    print("fonte_dados/ e raw/ foram sincronizadas.")


if __name__ == "__main__":
    main()