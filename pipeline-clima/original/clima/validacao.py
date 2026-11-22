"""Subsistema de validação: mede a qualidade dos dados brutos sem alterá-los."""

from dataclasses import dataclass, field

import pandas as pd

from .config import COLUNAS


class ErroValidacao(Exception):
    """Dados em formato que o pipeline não sabe tratar."""


@dataclass
class RelatorioValidacao:
    linhas: int
    duplicadas: int
    nulos: dict[str, int] = field(default_factory=dict)
    fora_da_faixa: int = 0
    tmin_maior_que_tmax: int = 0

    @property
    def problemas(self) -> int:
        return (
            self.duplicadas
            + sum(self.nulos.values())
            + self.fora_da_faixa
            + self.tmin_maior_que_tmax
        )


class Validador:
    """Confere esquema e faixas plausíveis para o clima do Sudeste."""

    def __init__(self, temp_min: float = -10.0, temp_max: float = 50.0, chuva_max: float = 500.0):
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.chuva_max = chuva_max

    def validar(self, df: pd.DataFrame) -> RelatorioValidacao:
        faltando = set(COLUNAS) - set(df.columns)
        if faltando:
            raise ErroValidacao(f"Colunas ausentes: {sorted(faltando)}")

        temps = df[["tmax", "tmin"]]
        fora = (temps < self.temp_min) | (temps > self.temp_max)
        chuva_fora = (df["chuva_mm"] < 0) | (df["chuva_mm"] > self.chuva_max)

        return RelatorioValidacao(
            linhas=len(df),
            duplicadas=int(df.duplicated(subset=["cidade", "data"]).sum()),
            nulos={c: int(n) for c, n in df[COLUNAS].isna().sum().items() if n},
            fora_da_faixa=int(fora.any(axis=1).sum() + chuva_fora.sum()),
            tmin_maior_que_tmax=int((df["tmin"] > df["tmax"]).sum()),
        )
