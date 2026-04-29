# MGPEB: Módulo de Gerenciamento de Pouso e Estabilização de Base

**Missão Aurora Siger · Fase 2 · FIAP · Ciência da Computação · 2026**

Protótipo do sistema responsável por organizar pousos de módulos da colônia Aurora Siger em Marte, tomando decisões automatizadas com base em lógica booleana, estruturas de dados lineares e algoritmos clássicos de busca e ordenação.

---

## Entregáveis

| Arquivo | Descrição |
|---|---|
| `mgpeb.py` | Código-fonte do protótipo MGPEB |
| `relatorio_mgpeb_aurora_siger_fase2.pdf` | Relatório técnico (10 páginas) |

---

## Como executar

Requer Python 3.10 ou superior.

```bash
# Demonstração automática completa
python3 mgpeb.py --demo

# Modo interativo (menu)
python3 mgpeb.py
```

---

## O que o sistema implementa

**Lógica booleana**
- Portas AND, OR, NOT, NAND, NOR, XOR
- Autorização de pouso baseada em expressões booleanas compostas

**Estruturas de dados lineares**
- Fila (`fila_autorizacao`) · FIFO para sequência de pousos
- Pilha (`pilha_log`) · LIFO para auditoria de operações
- Listas (`lista_pousados`, `lista_alertas`) · destino final dos módulos

**Algoritmos de ordenação (O(n²))**
- Bubble Sort · ordena por prioridade
- Selection Sort · ordena por combustível
- Insertion Sort · ordena por ETA orbital

**Algoritmos de busca**
- Busca linear O(n) · por nome do módulo
- Busca binária O(log n) · por ETA (requer lista ordenada)

**Modelagem matemática**
- `h(t) = 8000 − 180t − 1,86t²` · altitude de descida (quadrática)
- `E(t) = 4,2 · sin(π · t / 24,6)` · energia solar (senoidal)
- `C(v) = 0,5 + 0,003 · v²` · consumo de combustível (quadrática)
- `T(t) = −63 + 30 · sin(2π · t / 88775)` · temperatura externa (senoidal)

---

## Módulos da missão

| ID | Tipo | Prioridade | Combustível | Criticidade |
|---|---|---|---|---|
| ENE-01 | Energia | 1 | 82,1% | CRÍTICA |
| MED-01 | Suporte Médico | 1 | 91,0% | CRÍTICA |
| HAB-01 | Habitação | 2 | 68,4% | ALTA |
| LAB-01 | Lab. Científico | 3 | 55,7% | MÉDIA |
| LOG-01 | Logística | 4 | 17,3% ⚠ | MÉDIA |

---

**Aluno:** Paulo Roberto Faulstich Rego  
**Grupo:** 61  
**Contato:** paulo.faulstich@gmail.com
