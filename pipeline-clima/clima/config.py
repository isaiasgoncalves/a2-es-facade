"""Configuração compartilhada: cidades conhecidas e colunas padronizadas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Cidade:
    nome: str
    latitude: float
    longitude: float


CIDADES = {
    "Rio de Janeiro": Cidade("Rio de Janeiro", -22.91, -43.17),
    "São Paulo": Cidade("São Paulo", -23.55, -46.63),
    "Belo Horizonte": Cidade("Belo Horizonte", -19.92, -43.94),
}

# Formato que todos os subsistemas esperam depois da extração.
COLUNAS = ["cidade", "data", "tmax", "tmin", "chuva_mm"]
