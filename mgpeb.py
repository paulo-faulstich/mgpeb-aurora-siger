"""
MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base
Missão Aurora Siger | Fase 2 | FIAP — Ciência da Computação
Aluno: Paulo Roberto Faulstich Rego | Grupo 61
"""

import math
import time
import random

# =============================================================================
# ESTRUTURAS DE DADOS — Módulos de pouso
# =============================================================================

# Cada módulo é representado como um dicionário com os seguintes atributos:
#   nome            : identificador do módulo
#   tipo            : categoria funcional
#   prioridade      : 1 (máxima) a 5 (mínima) — ordena a fila de pouso
#   combustivel     : percentual restante (0–100 %)
#   massa           : massa total em kg
#   criticidade     : nível de urgência da carga ("CRITICA","ALTA","MEDIA","BAIXA")
#   eta_min         : minutos até janela orbital (quando chega à órbita baixa)
#   sensores_ok     : True se todos os sensores de navegação estão operacionais
#   area_livre      : True se a área de pouso designada está desocupada

MODULOS_INICIAIS = [
    {
        "nome": "HAB-01",
        "tipo": "Habitação",
        "prioridade": 2,
        "combustivel": 68.4,
        "massa": 4200,
        "criticidade": "ALTA",
        "eta_min": 45,
        "sensores_ok": True,
        "area_livre": True,
    },
    {
        "nome": "ENE-01",
        "tipo": "Energia",
        "prioridade": 1,
        "combustivel": 82.1,
        "massa": 3100,
        "criticidade": "CRITICA",
        "eta_min": 20,
        "sensores_ok": True,
        "area_livre": True,
    },
    {
        "nome": "LAB-01",
        "tipo": "Laboratório Científico",
        "prioridade": 3,
        "combustivel": 55.7,
        "massa": 2800,
        "criticidade": "MEDIA",
        "eta_min": 90,
        "sensores_ok": True,
        "area_livre": True,
    },
    {
        "nome": "LOG-01",
        "tipo": "Logística",
        "prioridade": 4,
        "combustivel": 17.3,   # combustível crítico — abaixo do mínimo
        "massa": 5500,
        "criticidade": "MEDIA",
        "eta_min": 110,
        "sensores_ok": False,   # sensor com falha — bloqueará pouso
        "area_livre": True,
    },
    {
        "nome": "MED-01",
        "tipo": "Suporte Médico",
        "prioridade": 1,
        "combustivel": 91.0,
        "massa": 1900,
        "criticidade": "CRITICA",
        "eta_min": 15,
        "sensores_ok": True,
        "area_livre": True,
    },
]

# ─── Estruturas lineares ──────────────────────────────────────────────────────

# FILA (queue) — módulos aguardando autorização de pouso (FIFO)
fila_autorizacao = []

# LISTA — módulos já pousados com sucesso
lista_pousados = []

# LISTA — módulos em alerta (combustível baixo ou sensor falho)
lista_alertas = []

# PILHA (stack) — log de operações realizadas (LIFO)
pilha_log = []


# =============================================================================
# FUNÇÕES AUXILIARES — Pilha de log
# =============================================================================

def log_push(mensagem: str) -> None:
    """Empilha uma mensagem de log com timestamp."""
    entrada = f"[T+{len(pilha_log):03d}] {mensagem}"
    pilha_log.append(entrada)


def log_pop() -> str:
    """Desempilha a última mensagem do log (LIFO)."""
    if pilha_log:
        return pilha_log.pop()
    return "(log vazio)"


def log_topo() -> str:
    """Espia o topo da pilha sem remover."""
    if pilha_log:
        return pilha_log[-1]
    return "(log vazio)"


# =============================================================================
# PORTAS LÓGICAS BOOLEANAS
# =============================================================================

def porta_and(a: bool, b: bool) -> bool:
    """Porta AND: saída 1 somente quando ambas as entradas são 1."""
    return a and b


def porta_or(a: bool, b: bool) -> bool:
    """Porta OR: saída 1 quando pelo menos uma entrada é 1."""
    return a or b


def porta_not(a: bool) -> bool:
    """Porta NOT: inverte o sinal de entrada."""
    return not a


def porta_nand(a: bool, b: bool) -> bool:
    """Porta NAND: AND negado."""
    return not (a and b)


def porta_nor(a: bool, b: bool) -> bool:
    """Porta NOR: OR negado."""
    return not (a or b)


def porta_xor(a: bool, b: bool) -> bool:
    """Porta XOR: saída 1 quando as entradas são diferentes."""
    return a != b


# =============================================================================
# REGRAS DE DECISÃO — Autorização de pouso (lógica booleana)
# =============================================================================

# Expressão completa:
#   AUTORIZADO = combustivel_ok AND sensores_ok AND area_livre
#                AND (urgencia_alta OR combustivel_critico OR prioridade_maxima)
#
# Onde:
#   combustivel_ok      = combustivel >= 20 %
#   urgencia_alta       = criticidade in ("CRITICA", "ALTA")
#   combustivel_critico = combustivel < 30 %   (emergência — força tentativa)
#   prioridade_maxima   = prioridade == 1

def avaliar_autorizacao(modulo: dict) -> tuple[bool, str]:
    """
    Avalia se um módulo pode ser autorizado a pousar.

    Retorna (autorizado: bool, justificativa: str).
    Usa composição de portas lógicas para refletir o diagrama booleano.
    """
    comb_ok     = modulo["combustivel"] >= 20.0
    sensores_ok = modulo["sensores_ok"]
    area_ok     = modulo["area_livre"]
    urgencia    = modulo["criticidade"] in ("CRITICA", "ALTA")
    comb_crit   = modulo["combustivel"] < 30.0
    prior_max   = modulo["prioridade"] == 1

    # Condições de segurança — todas devem ser verdadeiras (AND)
    seguranca_ok = porta_and(porta_and(comb_ok, sensores_ok), area_ok)

    # Ao menos uma condição de urgência/prioridade (OR)
    urgencia_ok = porta_or(porta_or(urgencia, comb_crit), prior_max)

    # Decisão final
    autorizado = porta_and(seguranca_ok, urgencia_ok)

    # Justificativa textual para o relatório
    motivos = []
    if not comb_ok:
        motivos.append(f"combustível insuficiente ({modulo['combustivel']:.1f}% < 20%)")
    if not sensores_ok:
        motivos.append("sensores de navegação com falha")
    if not area_ok:
        motivos.append("área de pouso ocupada")
    if not urgencia_ok:
        motivos.append("sem urgência ou prioridade máxima declarada")

    if autorizado:
        justificativa = "AUTORIZADO — todas as condições de segurança atendidas"
    else:
        justificativa = "BLOQUEADO — " + "; ".join(motivos)

    return autorizado, justificativa


# =============================================================================
# ALGORITMOS DE BUSCA
# =============================================================================

def busca_linear(lista: list, chave: str, campo: str = "nome") -> int:
    """
    Busca linear O(n): percorre a lista do início ao fim.
    Retorna o índice do primeiro elemento encontrado, ou -1.
    """
    for i, modulo in enumerate(lista):
        if str(modulo[campo]).upper() == str(chave).upper():
            return i
    return -1


def busca_binaria(lista_ordenada: list, chave_eta: int) -> int:
    """
    Busca binária O(log n): requer lista ordenada por 'eta_min'.
    Retorna o índice do módulo com eta_min == chave_eta, ou -1.
    """
    inicio, fim = 0, len(lista_ordenada) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        val  = lista_ordenada[meio]["eta_min"]
        if val == chave_eta:
            return meio
        elif val < chave_eta:
            inicio = meio + 1
        else:
            fim = meio - 1
    return -1


# =============================================================================
# ALGORITMOS DE ORDENAÇÃO
# =============================================================================

def bubble_sort_prioridade(lista: list) -> list:
    """
    Bubble Sort O(n²): ordena módulos por prioridade (1=máxima).
    Trabalha sobre uma cópia da lista para não alterar o original.
    """
    arr = list(lista)
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if arr[j]["prioridade"] > arr[j + 1]["prioridade"]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def selection_sort_combustivel(lista: list) -> list:
    """
    Selection Sort O(n²): ordena módulos pelo combustível (menor primeiro).
    Útil para identificar quais módulos precisam pousar primeiro por emergência.
    """
    arr = list(lista)
    n = len(arr)
    for i in range(n):
        idx_min = i
        for j in range(i + 1, n):
            if arr[j]["combustivel"] < arr[idx_min]["combustivel"]:
                idx_min = j
        arr[i], arr[idx_min] = arr[idx_min], arr[i]
    return arr


def insertion_sort_eta(lista: list) -> list:
    """
    Insertion Sort O(n²): ordena módulos pelo ETA (menor ETA = chega primeiro).
    Necessário para habilitar a busca binária por janela orbital.
    """
    arr = list(lista)
    for i in range(1, len(arr)):
        chave = arr[i]
        j = i - 1
        while j >= 0 and arr[j]["eta_min"] > chave["eta_min"]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = chave
    return arr


# =============================================================================
# FUNÇÕES MATEMÁTICAS — Modelagem física do pouso
# =============================================================================

def altura_descida(t: float, h0: float = 8000.0, v0: float = 180.0,
                   a: float = -3.7) -> float:
    """
    Função quadrática — altura da nave durante a descida (m).

    h(t) = h0 + v0*t + 0.5*a*t²

    Parâmetros:
        h0 : altitude inicial (m) — 8 km acima da superfície marciana
        v0 : velocidade vertical inicial (m/s) — negativa = descendo
        a  : aceleração (m/s²) — g_marte ≈ 3.72 m/s²
        t  : tempo (s)
    """
    return h0 + v0 * t + 0.5 * a * t ** 2


def temperatura_externa(t: float, T0: float = -63.0, amp: float = 30.0,
                        periodo: float = 88775.0) -> float:
    """
    Função senoidal — variação da temperatura externa marciana (°C).

    T(t) = T0 + amp * sin(2π * t / período)

    Parâmetros:
        T0      : temperatura média de Marte (-63 °C)
        amp     : amplitude da variação diária (±30 °C)
        periodo : duração do dia marciano em segundos (88.775 s ≈ 24h 37min)
        t       : tempo em segundos desde o meio-dia marciano
    """
    return T0 + amp * math.sin(2 * math.pi * t / periodo)


def consumo_combustivel(v: float, c0: float = 0.5, k: float = 0.003) -> float:
    """
    Função quadrática — consumo de combustível (kg/s) em função da velocidade.

    C(v) = c0 + k * v²

    Parâmetros:
        c0 : consumo mínimo em repouso (0.5 kg/s — propulsores de estabilização)
        k  : coeficiente de resistência atmosférica marciana
        v  : velocidade de descida (m/s)
    """
    return c0 + k * v ** 2


def energia_solar(t_horas: float, E_max: float = 4.2) -> float:
    """
    Função senoidal — geração de energia solar ao longo do dia marciano (kW).

    E(t) = max(0, E_max * sin(π * t / 24.6))

    Parâmetros:
        E_max    : pico de geração solar (4.2 kW por painel em Marte)
        t_horas  : hora do dia marciano (0–24.6 h)
    """
    return max(0.0, E_max * math.sin(math.pi * t_horas / 24.6))


# =============================================================================
# INICIALIZAÇÃO DO SISTEMA
# =============================================================================

def inicializar_sistema() -> None:
    """
    Popula a fila de autorização com os módulos iniciais.
    Separa módulos em alerta antes de enfileirá-los.
    """
    for modulo in MODULOS_INICIAIS:
        em_alerta = (modulo["combustivel"] < 20.0 or not modulo["sensores_ok"])
        if em_alerta:
            lista_alertas.append(modulo)
            log_push(f"ALERTA: {modulo['nome']} adicionado à lista de alertas")
        else:
            fila_autorizacao.append(modulo)     # enqueue
            log_push(f"FILA: {modulo['nome']} enfileirado para autorização")


# =============================================================================
# EXIBIÇÃO — Formatação de tabelas no terminal
# =============================================================================

SEP = "─" * 80


def cabecalho(titulo: str) -> None:
    print(f"\n{SEP}")
    print(f"  {titulo}")
    print(SEP)


def exibir_modulo(m: dict, idx: int = None) -> None:
    prefixo = f"[{idx}] " if idx is not None else "    "
    comb_flag = " ⚠" if m["combustivel"] < 20 else ""
    sens_flag = " ✖" if not m["sensores_ok"] else ""
    print(f"{prefixo}{m['nome']:8s} | {m['tipo']:22s} | "
          f"Prio:{m['prioridade']} | Comb:{m['combustivel']:5.1f}%{comb_flag} | "
          f"ETA:{m['eta_min']:4d}min | {m['criticidade']:6s}{sens_flag}")


def exibir_lista(lista: list, titulo: str) -> None:
    cabecalho(titulo)
    if not lista:
        print("  (vazia)")
        return
    for i, m in enumerate(lista):
        exibir_modulo(m, i)


# =============================================================================
# OPERAÇÕES PRINCIPAIS DO MGPEB
# =============================================================================

def processar_proximo_pouso() -> None:
    """
    Dequeue: retira o próximo módulo da fila, avalia autorização e roteia.
    """
    cabecalho("PROCESSANDO PRÓXIMO POUSO")
    if not fila_autorizacao:
        print("  Fila de autorização vazia.")
        return

    modulo = fila_autorizacao.pop(0)   # dequeue (FIFO)
    print(f"\n  Módulo em análise: {modulo['nome']} — {modulo['tipo']}")
    autorizado, justificativa = avaliar_autorizacao(modulo)
    print(f"  Avaliação: {justificativa}")

    if autorizado:
        lista_pousados.append(modulo)
        log_push(f"POUSO OK: {modulo['nome']} autorizado e pousado")
        print(f"  ✔ {modulo['nome']} transferido para lista de módulos pousados.")
    else:
        lista_alertas.append(modulo)
        log_push(f"BLOQUEIO: {modulo['nome']} — {justificativa}")
        print(f"  ✖ {modulo['nome']} transferido para lista de alertas.")


def reordenar_fila(criterio: str) -> None:
    """
    Reordena a fila de autorização pelo critério escolhido.
    Critérios: 'prioridade', 'combustivel', 'eta'.
    """
    global fila_autorizacao
    cabecalho(f"REORDENANDO FILA — critério: {criterio.upper()}")
    if criterio == "prioridade":
        fila_autorizacao = bubble_sort_prioridade(fila_autorizacao)
        print("  Bubble Sort aplicado — fila reordenada por prioridade (1=máxima).")
    elif criterio == "combustivel":
        fila_autorizacao = selection_sort_combustivel(fila_autorizacao)
        print("  Selection Sort aplicado — módulos com menos combustível primeiro.")
    elif criterio == "eta":
        fila_autorizacao = insertion_sort_eta(fila_autorizacao)
        print("  Insertion Sort aplicado — fila reordenada por janela orbital (ETA).")
    else:
        print("  Critério inválido. Use: prioridade | combustivel | eta")
        return
    log_push(f"ORDENAÇÃO: fila reordenada por {criterio}")
    for m in fila_autorizacao:
        exibir_modulo(m)


def buscar_modulo() -> None:
    """Menu de busca: linear por nome ou binária por ETA."""
    cabecalho("BUSCA DE MÓDULO")
    print("  1. Busca linear por nome")
    print("  2. Busca binária por ETA (min)")
    op = input("\n  Opção: ").strip()

    if op == "1":
        nome = input("  Nome do módulo (ex: HAB-01): ").strip()
        # Busca em todas as listas
        for lista, rotulo in [(fila_autorizacao, "Fila"), (lista_pousados, "Pousados"),
                               (lista_alertas, "Alertas")]:
            idx = busca_linear(lista, nome)
            if idx != -1:
                print(f"\n  Encontrado em [{rotulo}] posição {idx}:")
                exibir_modulo(lista[idx])
                return
        print("  Módulo não encontrado.")

    elif op == "2":
        try:
            eta = int(input("  ETA em minutos: ").strip())
        except ValueError:
            print("  Valor inválido.")
            return
        ordenada = insertion_sort_eta(fila_autorizacao)
        idx = busca_binaria(ordenada, eta)
        if idx != -1:
            print(f"\n  Encontrado (busca binária) na posição {idx} da fila ordenada:")
            exibir_modulo(ordenada[idx])
        else:
            print(f"  Nenhum módulo com ETA exato de {eta} min.")


def simular_funcoes_matematicas() -> None:
    """
    Exibe os valores das funções matemáticas para parâmetros de pouso.
    Simula a descida de um módulo ao longo do tempo.
    """
    cabecalho("SIMULAÇÃO DE FUNÇÕES MATEMÁTICAS — MÓDULO ENE-01")

    print("\n  ── Descida (h(t) = 8000 - 180t - 1.85t²) ──")
    print(f"  {'t(s)':>6}  {'Altitude(m)':>12}  {'Temp ext(°C)':>13}  {'Consumo(kg/s)':>14}")
    print(f"  {'─'*6}  {'─'*12}  {'─'*13}  {'─'*14}")

    v_descida = -180.0   # m/s (negativo = descendo)
    for t in range(0, 46, 5):
        h   = altura_descida(t, h0=8000, v0=v_descida, a=-3.72)
        if h < 0:
            h = 0
        T   = temperatura_externa(t * 60, T0=-63.0, amp=30.0)
        vel = abs(v_descida + (-3.72) * t)
        C   = consumo_combustivel(vel)
        print(f"  {t:>6}  {h:>12.1f}  {T:>13.2f}  {C:>14.3f}")

    print("\n  ── Energia Solar ao longo do dia marciano (24.6 h) ──")
    print(f"  {'Hora':>5}  {'E(kW)':>7}")
    print(f"  {'─'*5}  {'─'*7}")
    for h in range(0, 26, 2):
        e = energia_solar(h)
        barra = "█" * int(e * 4)
        print(f"  {h:>5}h  {e:>5.2f}  {barra}")

    log_push("SIMULAÇÃO: funções matemáticas executadas")


def exibir_log() -> None:
    """Exibe o log de operações sem desempilhar."""
    cabecalho("LOG DE OPERAÇÕES (PILHA — visualização)")
    if not pilha_log:
        print("  (vazio)")
        return
    for entrada in reversed(pilha_log):
        print(f"  {entrada}")


def tabela_verdade_portas() -> None:
    """Exibe a tabela-verdade das portas lógicas usadas no MGPEB."""
    cabecalho("TABELA-VERDADE — PORTAS LÓGICAS DO MGPEB")
    print(f"\n  {'A':>1}  {'B':>1}  {'AND':>4}  {'OR':>4}  {'NAND':>5}  "
          f"{'NOR':>5}  {'XOR':>5}  {'NOT A':>6}")
    print(f"  {'─':>1}  {'─':>1}  {'─'*4}  {'─'*4}  {'─'*5}  {'─'*5}  "
          f"{'─'*5}  {'─'*6}")
    for a in [False, True]:
        for b in [False, True]:
            print(f"  {int(a):>1}  {int(b):>1}  "
                  f"{int(porta_and(a,b)):>4}  {int(porta_or(a,b)):>4}  "
                  f"{int(porta_nand(a,b)):>5}  {int(porta_nor(a,b)):>5}  "
                  f"{int(porta_xor(a,b)):>5}  {int(porta_not(a)):>6}")


def processar_fila_completa() -> None:
    """Processa todos os módulos da fila automaticamente."""
    cabecalho("PROCESSAMENTO AUTOMÁTICO — FILA COMPLETA")
    if not fila_autorizacao:
        print("  Fila vazia.")
        return
    while fila_autorizacao:
        processar_proximo_pouso()


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

MENU = """
╔══════════════════════════════════════════════════════════════════════════════╗
║           MGPEB — Módulo de Gerenciamento de Pouso e Estabilização          ║
║                     Missão Aurora Siger · Fase 2 · FIAP                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  1. Exibir fila de autorização                                               ║
║  2. Exibir módulos pousados                                                  ║
║  3. Exibir módulos em alerta                                                 ║
║  4. Processar próximo pouso (dequeue)                                        ║
║  5. Processar fila completa                                                  ║
║  6. Reordenar fila (prioridade / combustivel / eta)                          ║
║  7. Buscar módulo                                                             ║
║  8. Tabela-verdade das portas lógicas                                        ║
║  9. Simular funções matemáticas de pouso                                     ║
║  L. Exibir log de operações                                                  ║
║  0. Sair                                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


def menu_principal() -> None:
    inicializar_sistema()
    print(MENU)
    log_push("SISTEMA: MGPEB inicializado")

    while True:
        opcao = input("\nOpção > ").strip().upper()

        match opcao:
            case "1":
                exibir_lista(fila_autorizacao, "FILA DE AUTORIZAÇÃO")
            case "2":
                exibir_lista(lista_pousados, "MÓDULOS POUSADOS")
            case "3":
                exibir_lista(lista_alertas, "MÓDULOS EM ALERTA")
            case "4":
                processar_proximo_pouso()
            case "5":
                processar_fila_completa()
            case "6":
                crit = input("  Critério (prioridade/combustivel/eta): ").strip().lower()
                reordenar_fila(crit)
            case "7":
                buscar_modulo()
            case "8":
                tabela_verdade_portas()
            case "9":
                simular_funcoes_matematicas()
            case "L":
                exibir_log()
            case "0":
                print("\n  Encerrando MGPEB. Missão Aurora Siger — Stay on course.\n")
                break
            case _:
                print("  Opção inválida.")


# =============================================================================
# EXECUÇÃO DIRETA — demonstração automática para evidências
# =============================================================================

def executar_demonstracao() -> None:
    """
    Executa uma sequência demonstrativa completa do MGPEB.
    Gera todas as evidências de execução necessárias para o relatório.
    """
    print("=" * 80)
    print("  MGPEB — DEMONSTRAÇÃO AUTOMÁTICA COMPLETA")
    print("  Missão Aurora Siger | Fase 2 | FIAP")
    print("=" * 80)

    inicializar_sistema()
    log_push("SISTEMA: demonstração automática iniciada")

    # 1. Estado inicial
    exibir_lista(fila_autorizacao, "ESTADO INICIAL — FILA DE AUTORIZAÇÃO")
    exibir_lista(lista_alertas, "ESTADO INICIAL — MÓDULOS EM ALERTA")

    # 2. Tabela-verdade
    tabela_verdade_portas()

    # 3. Reordenar por prioridade
    reordenar_fila("prioridade")

    # 4. Processar fila completa
    processar_fila_completa()

    # 5. Estado final
    exibir_lista(lista_pousados, "ESTADO FINAL — MÓDULOS POUSADOS")
    exibir_lista(lista_alertas, "ESTADO FINAL — MÓDULOS EM ALERTA")

    # 6. Busca linear
    cabecalho("BUSCA LINEAR — procurando MED-01 na lista de pousados")
    idx = busca_linear(lista_pousados, "MED-01")
    if idx != -1:
        print(f"  MED-01 encontrado na posição {idx}:")
        exibir_modulo(lista_pousados[idx])
    else:
        print("  MED-01 não encontrado na lista de pousados.")

    # 7. Busca binária (necessita lista ordenada por ETA)
    cabecalho("BUSCA BINÁRIA — procurando módulo com ETA = 20 min")
    todos = fila_autorizacao + lista_pousados + lista_alertas
    ordenada_eta = insertion_sort_eta(todos)
    idx2 = busca_binaria(ordenada_eta, 20)
    if idx2 != -1:
        print(f"  Módulo com ETA 20 min encontrado na posição {idx2}:")
        exibir_modulo(ordenada_eta[idx2])
    else:
        print("  Nenhum módulo com ETA exato de 20 min.")

    # 8. Ordenação por combustível
    cabecalho("SELECTION SORT — todos os módulos ordenados por combustível")
    todos_comb = selection_sort_combustivel(todos)
    for m in todos_comb:
        exibir_modulo(m)

    # 9. Funções matemáticas
    simular_funcoes_matematicas()

    # 10. Log completo
    exibir_log()

    print(f"\n{SEP}")
    print("  DEMONSTRAÇÃO CONCLUÍDA — todos os módulos processados.")
    print(SEP)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        executar_demonstracao()
    else:
        menu_principal()
