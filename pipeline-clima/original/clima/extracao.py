"""Subsistema de extração: de onde os dados vêm.

As duas fontes têm a mesma interface (`buscar`), então a fachada pode trocar
uma pela outra sem que o cliente perceba.
"""

import pandas as pd
import requests

from .config import COLUNAS, Cidade


class FonteOpenMeteo:
    """Busca dados diários na API histórica do Open-Meteo (gratuita, sem chave)."""

    URL = "https://archive-api.open-meteo.com/v1/archive"
    VARIAVEIS = "temperature_2m_max,temperature_2m_min,precipitation_sum"

    def __init__(self, timeout: int = 30, sessao: requests.Session | None = None):
        self.timeout = timeout
        self.sessao = sessao or requests.Session()

    def buscar(self, cidade: Cidade, inicio: str, fim: str) -> pd.DataFrame:
        resposta = self.sessao.get(
            self.URL,
            params={
                "latitude": cidade.latitude,
                "longitude": cidade.longitude,
                "start_date": inicio,
                "end_date": fim,
                "daily": self.VARIAVEIS,
                "timezone": "America/Sao_Paulo",
            },
            timeout=self.timeout,
        )
        resposta.raise_for_status()
        diario = resposta.json()["daily"]
        return pd.DataFrame(
            {
                "cidade": cidade.nome,
                "data": diario["time"],
                "tmax": diario["temperature_2m_max"],
                "tmin": diario["temperature_2m_min"],
                "chuva_mm": diario["precipitation_sum"],
            }
        )


class FonteCSV:
    """Lê um CSV local no formato padronizado. Serve para rodar offline."""

    def __init__(self, caminho: str):
        self.caminho = caminho
        self._cache: pd.DataFrame | None = None

    def buscar(self, cidade: Cidade, inicio: str, fim: str) -> pd.DataFrame:
        if self._cache is None:
            self._cache = pd.read_csv(self.caminho)
        df = self._cache
        filtro = (df["cidade"] == cidade.nome) & (df["data"] >= inicio) & (df["data"] <= fim)
        return df.loc[filtro, COLUNAS].copy()
