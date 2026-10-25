"""Testes offline: usam o CSV sujo e uma fonte falsa, nada de internet."""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from clima import PipelineClima
from clima.validacao import ErroValidacao, Validador

DADOS = Path(__file__).resolve().parents[1] / "dados"
CIDADES = ["Rio de Janeiro", "São Paulo", "Belo Horizonte"]


def test_pipeline_offline_limpa_e_persiste(tmp_path):
    resultado = PipelineClima.offline(DADOS / "clima_sujo.csv", tmp_path).executar(
        CIDADES, "2026-01-01", "2026-03-31"
    )

    assert resultado.validacao.problemas > 0
    assert resultado.diario[["tmax", "tmin", "chuva_mm"]].notna().all().all()
    assert not resultado.diario.duplicated(subset=["cidade", "data"]).any()
    assert (resultado.diario["tmin"] <= resultado.diario["tmax"]).all()
    assert len(resultado.mensal) == 9  # 3 cidades x 3 meses

    with sqlite3.connect(resultado.banco) as con:
        assert con.execute("SELECT COUNT(*) FROM clima_diario").fetchone()[0] == 270
    assert resultado.relatorio.exists()


def test_rodar_duas_vezes_nao_duplica(tmp_path):
    pipeline = PipelineClima.offline(DADOS / "clima_amostra.csv", tmp_path)
    pipeline.executar(CIDADES, "2026-01-01", "2026-01-31")
    pipeline.executar(CIDADES, "2026-01-01", "2026-01-31")
    with sqlite3.connect(tmp_path / "clima.db") as con:
        assert con.execute("SELECT COUNT(*) FROM clima_diario").fetchone()[0] == 93


def test_trocar_fonte_nao_muda_o_cliente(tmp_path):
    class FonteFalsa:
        def buscar(self, cidade, inicio, fim):
            datas = pd.date_range(inicio, fim).strftime("%Y-%m-%d")
            return pd.DataFrame({"cidade": cidade.nome, "data": datas, "tmax": 30.0, "tmin": 20.0, "chuva_mm": 0.0})

    resultado = PipelineClima(fonte=FonteFalsa(), pasta_saida=tmp_path).executar(
        ["Rio de Janeiro"], "2026-02-01", "2026-02-28"
    )
    assert resultado.mensal["tmax_media"].tolist() == [30.0]


def test_validador_rejeita_esquema_errado():
    with pytest.raises(ErroValidacao):
        Validador().validar(pd.DataFrame({"cidade": ["Rio"]}))


def test_cidade_desconhecida(tmp_path):
    with pytest.raises(ValueError):
        PipelineClima.offline(DADOS / "clima_amostra.csv", tmp_path).executar(["Recife"], "2026-01-01", "2026-01-02")
