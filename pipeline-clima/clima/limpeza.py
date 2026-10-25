"""Subsistema de limpeza: transforma dados brutos em dados confiáveis.

A ordem dos passos importa: tipos antes de duplicatas, faixas antes da
interpolação. Esse é o tipo de detalhe que a fachada esconde do cliente.
"""

import numpy as np
import pandas as pd


class Limpador:
    def __init__(self, temp_min: float = -10.0, temp_max: float = 50.0, chuva_max: float = 500.0):
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.chuva_max = chuva_max

    def limpar(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["data"] = pd.to_datetime(df["data"])
        for col in ["tmax", "tmin", "chuva_mm"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.drop_duplicates(subset=["cidade", "data"], keep="first")
        df = df.sort_values(["cidade", "data"]).reset_index(drop=True)

        # Valores impossíveis viram ausentes e são tratados junto com os nulos.
        for col in ["tmax", "tmin"]:
            fora = (df[col] < self.temp_min) | (df[col] > self.temp_max)
            df.loc[fora, col] = np.nan
        df.loc[(df["chuva_mm"] < 0) | (df["chuva_mm"] > self.chuva_max), "chuva_mm"] = np.nan

        invertido = df["tmin"] > df["tmax"]
        df.loc[invertido, ["tmax", "tmin"]] = df.loc[invertido, ["tmin", "tmax"]].to_numpy()

        # Temperatura: interpola dentro de cada cidade. Chuva ausente: assume 0 mm.
        df[["tmax", "tmin"]] = df.groupby("cidade")[["tmax", "tmin"]].transform(
            lambda s: s.interpolate(limit_direction="both")
        )
        df["chuva_mm"] = df["chuva_mm"].fillna(0.0)
        return df
