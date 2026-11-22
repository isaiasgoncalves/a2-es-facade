"""Cliente 2: análise offline de um CSV recebido de outra fonte."""

from pathlib import Path

import pandas as pd

from clima.agregacao import Agregador
from clima.carga import RepositorioSQLite
from clima.config import CIDADES
from clima.extracao import FonteCSV
from clima.limpeza import Limpador
from clima.relatorio import GeradorRelatorio
from clima.validacao import Validador

CSV_PADRAO = Path(__file__).resolve().parents[1] / "dados" / "clima_sujo.csv"


def rodar(csv, cidades, inicio, fim, pasta_saida="saida") -> pd.DataFrame:
    pasta_saida = Path(pasta_saida)
    fonte = FonteCSV(str(csv))

    desconhecidas = [c for c in cidades if c not in CIDADES]
    if desconhecidas:
        raise ValueError(f"Cidades sem coordenadas cadastradas: {desconhecidas}")
    bruto = pd.concat([fonte.buscar(CIDADES[c], inicio, fim) for c in cidades], ignore_index=True)

    validacao = Validador().validar(bruto)
    print(validacao)
    diario = Limpador().limpar(bruto)
    mensal = Agregador().mensal(diario)

    repositorio = RepositorioSQLite(pasta_saida / "clima.db")
    repositorio.conectar()
    try:
        repositorio.criar_tabelas()
        repositorio.salvar("clima_diario", diario, ["cidade", "data"])
        repositorio.salvar("clima_mensal", mensal, ["cidade", "mes"])
    finally:
        repositorio.fechar()

    GeradorRelatorio(pasta_saida).gerar(mensal, validacao, fonte=type(fonte).__name__)
    return mensal


if __name__ == "__main__":
    mensal = rodar(CSV_PADRAO, ["Rio de Janeiro", "São Paulo", "Belo Horizonte"], "2026-01-01", "2026-03-31")
    print(mensal.to_string(index=False))
