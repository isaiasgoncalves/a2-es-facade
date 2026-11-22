"""Subsistema de carga: persiste os resultados num banco SQLite.

Tem um protocolo próprio: conectar, criar tabelas, salvar, fechar. Esquecer um
passo ou trocar a ordem quebra a carga.
"""

import sqlite3
from pathlib import Path

import pandas as pd

ESQUEMA = """
CREATE TABLE IF NOT EXISTS clima_diario (
    cidade TEXT NOT NULL,
    data TEXT NOT NULL,
    tmax REAL, tmin REAL, chuva_mm REAL,
    PRIMARY KEY (cidade, data)
);
CREATE TABLE IF NOT EXISTS clima_mensal (
    cidade TEXT NOT NULL,
    mes TEXT NOT NULL,
    tmax_media REAL, tmin_media REAL, amplitude_media REAL,
    chuva_total_mm REAL, dias_chuvosos INTEGER,
    PRIMARY KEY (cidade, mes)
);
"""


class RepositorioSQLite:
    def __init__(self, caminho: str | Path):
        self.caminho = Path(caminho)
        self.conexao: sqlite3.Connection | None = None

    def conectar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        self.conexao = sqlite3.connect(self.caminho)

    def criar_tabelas(self) -> None:
        self._exigir_conexao().executescript(ESQUEMA)

    def salvar(self, tabela: str, df: pd.DataFrame, chaves: list[str]) -> int:
        """Substitui as linhas com as mesmas chaves (upsert simples)."""
        con = self._exigir_conexao()
        df = df.copy()
        if "data" in df:
            df["data"] = df["data"].astype(str).str[:10]
        colunas = ", ".join(df.columns)
        marcadores = ", ".join("?" for _ in df.columns)
        con.executemany(
            f"INSERT OR REPLACE INTO {tabela} ({colunas}) VALUES ({marcadores})",
            df.itertuples(index=False, name=None),
        )
        con.commit()
        return len(df)

    def fechar(self) -> None:
        if self.conexao is not None:
            self.conexao.close()
            self.conexao = None

    def _exigir_conexao(self) -> sqlite3.Connection:
        if self.conexao is None:
            raise RuntimeError("Chame conectar() antes de usar o repositório.")
        return self.conexao
