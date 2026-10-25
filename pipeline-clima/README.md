# Pipeline de clima — com e sem Facade

Projeto do trabalho de Engenharia de Software sobre o padrão **Facade**. O mesmo pipeline de dados aparece em duas versões:

| Versão | Onde | Ideia |
| --- | --- | --- |
| Go horse | `notebooks/01_go_horse.ipynb` | Tudo num notebook, sem funções, URL colada no código, copia e cola para cada caso novo |
| Com Facade | `clima/` + `main.py` + `notebooks/02_com_facade.ipynb` | Seis subsistemas e uma fachada, `PipelineClima`, que expõe uma chamada só |

Referências do padrão: [Facade — Referências e trilha de estudo](../Facade%20—%20Referências%20e%20trilha%20de%20estudo.md).

## O pipeline

Temperatura máxima, mínima e chuva diárias de Rio de Janeiro, São Paulo e Belo Horizonte, de jan a mar/2026.

```
extrair (API Open-Meteo ou CSV) → validar → limpar → agregar por mês → gravar no SQLite → gerar relatório
```

## Estrutura

```
pipeline-clima/
├── clima/                  # versão com Facade
│   ├── facade.py           # PipelineClima: a fachada
│   ├── extracao.py         # FonteOpenMeteo, FonteCSV  (mesma interface: buscar)
│   ├── validacao.py        # Validador → RelatorioValidacao
│   ├── limpeza.py          # Limpador (a ordem dos passos importa)
│   ├── agregacao.py        # Agregador.mensal
│   ├── carga.py            # RepositorioSQLite (conectar → criar_tabelas → salvar → fechar)
│   ├── relatorio.py        # GeradorRelatorio (Markdown)
│   └── config.py           # cidades e colunas padronizadas
├── main.py                 # cliente de linha de comando: só conhece a fachada
├── notebooks/
│   ├── 01_go_horse.ipynb
│   └── 02_com_facade.ipynb
├── dados/
│   ├── clima_amostra.csv   # dados reais do Open-Meteo, para rodar offline
│   └── clima_sujo.csv      # a mesma amostra com defeitos injetados de propósito
└── tests/test_pipeline.py  # roda offline, com o CSV e uma fonte falsa
```

**Sobre `clima_sujo.csv`:** é a amostra real com defeitos colocados à mão para a demonstração: 3 nulos, `tmax` = 999 °C em São Paulo (31/01), chuva negativa, `tmin` e `tmax` trocados num dia e 3 linhas repetidas. Não são dados reais.

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest                                    # testes offline
python main.py                            # versão com Facade, lendo da API
python main.py --csv dados/clima_sujo.csv # offline, com os dados sujos
jupyter notebook notebooks/               # as duas versões lado a lado
```

As saídas (`clima.db`, `relatorio_clima.md`) vão para `saida/`, que fica fora do Git.

## Como a fachada aparece no código

```python
from clima import PipelineClima

PipelineClima().executar(["Rio de Janeiro"], "2026-01-01", "2026-03-31")         # API
PipelineClima.offline("dados/clima_sujo.csv").executar(["Rio de Janeiro"], ...)   # CSV
```

Mapeando para os participantes do Refactoring Guru:

| Participante | Neste projeto |
| --- | --- |
| Fachada | `PipelineClima` |
| Subsistema complexo | `FonteOpenMeteo`/`FonteCSV`, `Validador`, `Limpador`, `Agregador`, `RepositorioSQLite`, `GeradorRelatorio` |
| Cliente | `main.py`, `02_com_facade.ipynb`, os testes |
| Fachada adicional | ainda não existe; candidata natural: uma `RelatorioFacade` se o relatório ganhar gráficos e PDF |

Os subsistemas não importam a fachada e continuam utilizáveis direto. O último bloco de `02_com_facade.ipynb` mostra isso.

## Roteiro sugerido para a demonstração

1. Rodar `01_go_horse.ipynb` com a API: funciona.
2. Rodar a parte do CSV sujo: o resultado sai errado (SP, janeiro: máxima média de 59,2 °C) e ninguém percebe.
3. Rodar `02_com_facade.ipynb`: o mesmo caso é uma linha a mais, o validador acusa 9 problemas e o resultado sai certo (26,9 °C).
4. Mostrar a troca de fonte no teste `test_trocar_fonte_nao_muda_o_cliente`.
5. Fechar com o contra: a fachada pode virar *god object* se tudo for para dentro dela.
