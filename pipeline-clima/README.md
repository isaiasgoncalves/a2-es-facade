# Pipeline de clima — antes e depois do Facade

Trabalho A2 de Engenharia de Software (FGV EMAp, 2026.2) sobre o padrão **Facade**.
O mesmo pipeline de dados existe em duas versões, com **os mesmos subsistemas**:

| Versão | Pasta | Como os clientes usam o pipeline |
| --- | --- | --- |
| Original | `original/` | Cada cliente importa os subsistemas e monta a sequência na mão |
| Refatorada | `refatorado/` | Cada cliente faz uma chamada à fachada `PipelineClima` |

`diff -r original/clima refatorado/clima` mostra que a única diferença no pacote é o
`facade.py` (e o `__init__.py` que o exporta). O que muda são os clientes.

## O pipeline

Temperatura máxima, mínima e chuva diárias de Rio de Janeiro, São Paulo e Belo Horizonte,
de jan a mar/2026.

### Fluxo dos dados

```mermaid
flowchart TD
    SRC[("API Open-Meteo<br/>ou CSV local")]
    EXT["<b>Extração</b><br/>FonteOpenMeteo / FonteCSV<br/>buscar() por cidade"]
    BRUTO[/"bruto<br/>cidade, data, tmax, tmin, chuva_mm"/]
    VAL["<b>Validação</b><br/>Validador.validar()<br/>conta problemas, não altera"]
    RV[/"RelatorioValidacao<br/>duplicadas, nulos, fora da faixa,<br/>tmin > tmax"/]
    LIM["<b>Limpeza</b><br/>Limpador.limpar()<br/>remove duplicatas · valor impossível vira nulo<br/>destroca tmin/tmax · interpola temperatura<br/>chuva ausente = 0 mm"]
    DIA[/"diario<br/>uma linha por cidade e dia"/]
    AGR["<b>Agregação</b><br/>Agregador.mensal()<br/>médias, amplitude, chuva total,<br/>dias chuvosos (≥ 1 mm)"]
    MEN[/"mensal<br/>uma linha por cidade e mês"/]
    REP["<b>Carga</b><br/>RepositorioSQLite<br/>conectar → criar_tabelas → salvar → fechar"]
    DB[("saida/clima.db<br/>clima_diario · clima_mensal")]
    REL["<b>Relatório</b><br/>GeradorRelatorio.gerar()"]
    MD[("saida/relatorio_clima.md")]

    SRC --> EXT --> BRUTO
    BRUTO --> VAL --> RV
    BRUTO --> LIM --> DIA --> AGR --> MEN
    DIA --> REP
    MEN --> REP --> DB
    MEN --> REL
    RV --> REL
    REL --> MD
```

A validação só mede a qualidade do dado bruto; quem corrige é a limpeza. O relatório
junta duas saídas que vêm de ramos diferentes: o resumo mensal e o resultado da validação.

### Ordem das chamadas (versão refatorada)

O mesmo fluxo, visto a partir de uma chamada do cliente à fachada. `carregar()` para
depois da carga no banco; `executar()` faz tudo isso e ainda gera o relatório.

```mermaid
sequenceDiagram
    actor C as Cliente
    participant F as PipelineClima
    participant S as Fonte
    participant V as Validador
    participant L as Limpador
    participant A as Agregador
    participant R as RepositorioSQLite
    participant G as GeradorRelatorio

    C->>F: executar(cidades, inicio, fim)
    F->>F: carregar(...)
    Note over F: checa se as cidades existem<br/>(ValueError se não)
    loop cada cidade
        F->>S: buscar(cidade, inicio, fim)
        S-->>F: DataFrame
    end
    F->>V: validar(bruto)
    V-->>F: RelatorioValidacao
    F->>L: limpar(bruto)
    L-->>F: diario
    F->>A: mensal(diario)
    A-->>F: mensal
    F->>R: conectar()
    F->>R: criar_tabelas()
    F->>R: salvar(clima_diario) · salvar(clima_mensal)
    F->>R: fechar() (no finally)
    F->>G: gerar(mensal, validacao, fonte)
    G-->>F: caminho do relatório
    F-->>C: ResultadoPipeline
```

Na versão original não existe a coluna `PipelineClima`: é o próprio cliente que faz
cada uma dessas chamadas, na ordem.

| Subsistema | Arquivo | Responsabilidade |
| --- | --- | --- |
| `FonteOpenMeteo`, `FonteCSV` | `clima/extracao.py` | Buscar os dados diários (mesma interface: `buscar`) |
| `Validador` | `clima/validacao.py` | Medir a qualidade dos dados brutos sem alterá-los |
| `Limpador` | `clima/limpeza.py` | Tratar duplicatas, valores impossíveis, inversões e lacunas |
| `Agregador` | `clima/agregacao.py` | Resumir por cidade e mês |
| `RepositorioSQLite` | `clima/carga.py` | Gravar no banco (protocolo: `conectar → criar_tabelas → salvar → fechar`) |
| `GeradorRelatorio` | `clima/relatorio.py` | Escrever o relatório em Markdown |

## Arquitetura

**Original:** cada cliente fala direto com os subsistemas que usa, e cada um repete a
ordem das etapas e o protocolo do banco.

```mermaid
flowchart LR
    subgraph clientes["Clientes"]
        RM["relatorio_mensal.py"]
        AC["analise_csv.py"]
        CN["carga_noturna.py"]
    end

    subgraph clima["clima/ (subsistemas)"]
        API["FonteOpenMeteo"]
        CSV["FonteCSV"]
        VAL["Validador"]
        LIM["Limpador"]
        AGR["Agregador"]
        REP["RepositorioSQLite"]
        REL["GeradorRelatorio"]
    end

    RM --> API & VAL & LIM & AGR & REP & REL
    AC --> CSV & VAL & LIM & AGR & REP & REL
    CN --> API & LIM & AGR & REP
```

**Refatorada:** os clientes só conhecem a fachada `PipelineClima`, que cria os
subsistemas e os chama na ordem certa.

```mermaid
flowchart LR
    subgraph clientes["Clientes"]
        RM["relatorio_mensal.py"]
        AC["analise_csv.py"]
        CN["carga_noturna.py"]
        MAIN["main.py"]
    end

    F["PipelineClima<br/>(clima/facade.py)"]

    subgraph clima["clima/ (subsistemas, inalterados)"]
        API["FonteOpenMeteo"]
        CSV["FonteCSV"]
        VAL["Validador"]
        LIM["Limpador"]
        AGR["Agregador"]
        REP["RepositorioSQLite"]
        REL["GeradorRelatorio"]
    end

    RM -- "executar()" --> F
    AC -- "offline().executar()" --> F
    CN -- "carregar()" --> F
    MAIN -- "executar()" --> F
    F --> API & CSV & VAL & LIM & AGR & REP & REL
```

## Os três clientes

As duas versões têm os mesmos clientes, com os mesmos nomes e assinaturas:

| Cliente | Fonte | O que faz |
| --- | --- | --- |
| `relatorio_mensal.py` | API | Pipeline completo, com relatório |
| `analise_csv.py` | CSV local | Pipeline completo e imprime a validação |
| `carga_noturna.py` | API | Só até o banco, sem relatório |

## Estrutura

```
pipeline-clima/
├── original/
│   ├── clima/                  # subsistemas, sem fachada
│   └── relatorio_mensal.py, analise_csv.py, carga_noturna.py
├── refatorado/
│   ├── clima/                  # mesmos subsistemas + facade.py
│   ├── relatorio_mensal.py, analise_csv.py, carga_noturna.py
│   ├── main.py               
│   └── tests/test_pipeline.py  # testes da fachada
├── dados/
│   ├── clima_amostra.csv       # dados reais do Open-Meteo, para rodar offline
│   └── clima_sujo.csv          # a mesma amostra com defeitos injetados
└── tests/test_equivalencia.py  # original × refatorado
```

**Sobre `clima_sujo.csv`:** é a amostra real com defeitos colocados à mão para a
demonstração: 3 nulos, `tmax` = 999 °C em São Paulo (31/01), chuva negativa, `tmin` e
`tmax` trocados num dia e 3 linhas repetidas. Não são dados reais.

## Como rodar

Requer Python 3.10+ (testado em 3.11 e 3.14).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest                        # todos os testes, offline

cd original                   # ou: cd refatorado
python analise_csv.py         # offline, com o CSV sujo
python relatorio_mensal.py    # precisa de internet (API Open-Meteo)
python carga_noturna.py       # precisa de internet
```

As saídas (`clima.db`, `relatorio_clima.md`) vão para `saida/` dentro da pasta da versão,
fora do Git.

## Comportamento preservado

`tests/test_equivalencia.py` roda cada cliente nas duas versões com os dois CSVs
(6 casos) e confere que são iguais: o resumo mensal, as tabelas do banco, o relatório
(exceto a data de geração) e o que é impresso na tela. Como as duas versões têm um
pacote `clima`, cada uma roda num processo próprio.

Única diferença intencional: com uma cidade desconhecida, `original/carga_noturna.py`
gera `KeyError`, porque não faz a checagem que os outros dois clientes fazem. Na versão
refatorada, a checagem está na fachada e vale para todos (`ValueError`).

## Mapeamento para o padrão (Refactoring Guru)

| Participante | Neste projeto |
| --- | --- |
| Fachada | `PipelineClima` (`executar`, `carregar`, `offline`) |
| Subsistema complexo | as seis classes de `clima/` |
| Cliente | os três clientes, `main.py`, o notebook e os testes |
| Fachada adicional | ainda não existe; candidata natural: uma `RelatorioFacade` se o relatório ganhar gráficos e PDF |

Os subsistemas não importam a fachada e continuam utilizáveis direto.

## Integrantes

| Nome | Matrícula |
| --- | --- |
| Isaías Gouvêa Gonçalves | `<matrícula>` |
| Henrique Gasparelo | `<matrícula>` |
| Henrique Beltrão | `<matrícula>` |
| Mateus Mourão | `<matrícula>` |
| Thevez | `<matrícula>` |
