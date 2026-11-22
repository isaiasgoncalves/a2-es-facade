"""Cliente 3: carga noturna no banco, sem relatório."""

from pathlib import Path

import pandas as pd

from clima.agregacao import Agregador
from clima.carga import RepositorioSQLite
from clima.config import CIDADES
from clima.extracao import FonteOpenMeteo
from clima.limpeza import Limpador


def rodar(cidades, inicio, fim, pasta_saida="saida", fonte=None) -> pd.DataFrame:
    fonte = fonte or FonteOpenMeteo()
    bruto = pd.concat([fonte.buscar(CIDADES[c], inicio, fim) for c in cidades], ignore_index=True)

    diario = Limpador().limpar(bruto)
    mensal = Agregador().mensal(diario)

    repositorio = RepositorioSQLite(Path(pasta_saida) / "clima.db")
    repositorio.conectar()
    repositorio.criar_tabelas()
    repositorio.salvar("clima_diario", diario, ["cidade", "data"])
    repositorio.salvar("clima_mensal", mensal, ["cidade", "mes"])
    repositorio.fechar()
    return mensal


if __name__ == "__main__":
    mensal = rodar(["Rio de Janeiro", "São Paulo", "Belo Horizonte"], "2026-01-01", "2026-03-31")
    print(mensal.to_string(index=False))
