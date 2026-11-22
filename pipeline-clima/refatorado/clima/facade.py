"""A fachada: um ponto de entrada simples para o pipeline inteiro.

O cliente não precisa saber que existem seis subsistemas, em que ordem eles
rodam, nem que o repositório precisa ser aberto e fechado. Se uma peça mudar
(outra API, outro banco), só esta classe é ajustada.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .agregacao import Agregador
from .carga import RepositorioSQLite
from .config import CIDADES
from .extracao import FonteCSV, FonteOpenMeteo
from .limpeza import Limpador
from .relatorio import GeradorRelatorio
from .validacao import RelatorioValidacao, Validador

log = logging.getLogger(__name__)


@dataclass
class ResultadoPipeline:
    diario: pd.DataFrame
    mensal: pd.DataFrame
    validacao: RelatorioValidacao
    banco: Path
    relatorio: Path


class PipelineClima:
    def __init__(
        self,
        fonte: FonteOpenMeteo | FonteCSV | None = None,
        pasta_saida: str | Path = "saida",
        validador: Validador | None = None,
        limpador: Limpador | None = None,
        agregador: Agregador | None = None,
    ):
        # Como no Refactoring Guru: aceita subsistemas prontos ou cria os seus.
        pasta_saida = Path(pasta_saida)
        self.fonte = fonte or FonteOpenMeteo()
        self.validador = validador or Validador()
        self.limpador = limpador or Limpador()
        self.agregador = agregador or Agregador()
        self.repositorio = RepositorioSQLite(pasta_saida / "clima.db")
        self.relatorio = GeradorRelatorio(pasta_saida)

    @classmethod
    def offline(cls, csv: str | Path, pasta_saida: str | Path = "saida") -> "PipelineClima":
        """Atalho para rodar sem internet, lendo um CSV local."""
        return cls(fonte=FonteCSV(str(csv)), pasta_saida=pasta_saida)

    def executar(self, cidades: list[str], inicio: str, fim: str) -> ResultadoPipeline:
        bruto = self._extrair(cidades, inicio, fim)
        validacao = self.validador.validar(bruto)
        log.info("Validação: %d linhas, %d problemas", validacao.linhas, validacao.problemas)

        diario = self.limpador.limpar(bruto)
        mensal = self.agregador.mensal(diario)

        self.repositorio.conectar()
        try:
            self.repositorio.criar_tabelas()
            self.repositorio.salvar("clima_diario", diario, ["cidade", "data"])
            self.repositorio.salvar("clima_mensal", mensal, ["cidade", "mes"])
        finally:
            self.repositorio.fechar()

        caminho = self.relatorio.gerar(mensal, validacao, fonte=type(self.fonte).__name__)
        log.info("Relatório em %s", caminho)
        return ResultadoPipeline(diario, mensal, validacao, self.repositorio.caminho, caminho)

    def _extrair(self, cidades: list[str], inicio: str, fim: str) -> pd.DataFrame:
        desconhecidas = [c for c in cidades if c not in CIDADES]
        if desconhecidas:
            raise ValueError(f"Cidades sem coordenadas cadastradas: {desconhecidas}")
        partes = [self.fonte.buscar(CIDADES[c], inicio, fim) for c in cidades]
        return pd.concat(partes, ignore_index=True)
