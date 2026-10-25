"""Subsistema de agregação: resume os dados diários por cidade e mês."""

import pandas as pd


class Agregador:
    def __init__(self, limiar_dia_chuvoso_mm: float = 1.0):
        self.limiar = limiar_dia_chuvoso_mm

    def mensal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            mes=df["data"].dt.to_period("M").astype(str),
            amplitude=df["tmax"] - df["tmin"],
            dia_chuvoso=df["chuva_mm"] >= self.limiar,
        )
        return (
            df.groupby(["cidade", "mes"])
            .agg(
                tmax_media=("tmax", "mean"),
                tmin_media=("tmin", "mean"),
                amplitude_media=("amplitude", "mean"),
                chuva_total_mm=("chuva_mm", "sum"),
                dias_chuvosos=("dia_chuvoso", "sum"),
            )
            .round(1)
            .reset_index()
        )
