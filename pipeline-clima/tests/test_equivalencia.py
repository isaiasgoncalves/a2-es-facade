"""Prova de que a refatoração preservou o comportamento.

Cada cliente roda nas duas versões, com os mesmos dados e em pastas separadas.
Como as duas versões têm um pacote chamado `clima`, cada uma roda num processo
próprio, a partir da sua pasta.
"""

import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
CIDADES = ["Rio de Janeiro", "São Paulo", "Belo Horizonte"]

EXECUTOR = """
import sys
from clima.extracao import FonteCSV
import relatorio_mensal, analise_csv, carga_noturna

cliente, csv, saida, cidades = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
args = (cidades, "2026-01-01", "2026-03-31", saida)
if cliente == "analise_csv":
    mensal = analise_csv.rodar(csv, *args)
else:
    modulo = relatorio_mensal if cliente == "relatorio_mensal" else carga_noturna
    mensal = modulo.rodar(*args, fonte=FonteCSV(csv))
mensal.to_csv(f"{saida}/mensal.csv", index=False)
"""


def executar(versao: str, cliente: str, csv: Path, saida: Path) -> str:
    proc = subprocess.run(
        [sys.executable, "-c", EXECUTOR, cliente, str(csv), str(saida), ",".join(CIDADES)],
        cwd=RAIZ / versao, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def tabela(banco: Path, nome: str) -> pd.DataFrame:
    with closing(sqlite3.connect(banco)) as con:
        return pd.read_sql(f"SELECT * FROM {nome} ORDER BY 1, 2", con)


def relatorio_sem_data(pasta: Path) -> list[str] | None:
    caminho = pasta / "relatorio_clima.md"
    if not caminho.exists():
        return None
    return [l for l in caminho.read_text(encoding="utf-8").splitlines() if not l.startswith("Gerado em")]


@pytest.mark.parametrize("csv", ["clima_amostra.csv", "clima_sujo.csv"])
@pytest.mark.parametrize("cliente", ["relatorio_mensal", "analise_csv", "carga_noturna"])
def test_refatoracao_preserva_comportamento(cliente, csv, tmp_path):
    antes, depois = tmp_path / "original", tmp_path / "refatorado"
    stdout_antes = executar("original", cliente, DADOS / csv, antes)
    stdout_depois = executar("refatorado", cliente, DADOS / csv, depois)

    pd.testing.assert_frame_equal(pd.read_csv(antes / "mensal.csv"), pd.read_csv(depois / "mensal.csv"))
    for nome in ["clima_diario", "clima_mensal"]:
        pd.testing.assert_frame_equal(tabela(antes / "clima.db", nome), tabela(depois / "clima.db", nome))
    assert relatorio_sem_data(antes) == relatorio_sem_data(depois)
    assert stdout_antes == stdout_depois
