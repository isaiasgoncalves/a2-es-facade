"""Subsistema de relatório: escreve um resumo em Markdown."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .validacao import RelatorioValidacao


class GeradorRelatorio:
    def __init__(self, pasta: str | Path):
        self.pasta = Path(pasta)

    def gerar(self, mensal: pd.DataFrame, validacao: RelatorioValidacao, fonte: str) -> Path:
        self.pasta.mkdir(parents=True, exist_ok=True)
        caminho = self.pasta / "relatorio_clima.md"
        linhas = [
            "# Relatório de clima",
            "",
            f"Gerado em {datetime.now():%d/%m/%Y %H:%M} a partir de: {fonte}.",
            "",
            "## Qualidade dos dados brutos",
            "",
            f"- Linhas lidas: {validacao.linhas}",
            f"- Duplicadas: {validacao.duplicadas}",
            f"- Nulos: {validacao.nulos or 'nenhum'}",
            f"- Fora da faixa plausível: {validacao.fora_da_faixa}",
            f"- tmin maior que tmax: {validacao.tmin_maior_que_tmax}",
            "",
            "## Resumo mensal",
            "",
            _tabela_markdown(mensal),
            "",
        ]
        caminho.write_text("\n".join(linhas), encoding="utf-8")
        return caminho


def _tabela_markdown(df: pd.DataFrame) -> str:
    """Tabela Markdown simples, sem depender do pacote tabulate."""
    cabecalho = "| " + " | ".join(df.columns) + " |"
    separador = "| " + " | ".join("---" for _ in df.columns) + " |"
    corpo = ["| " + " | ".join(str(v) for v in linha) + " |" for linha in df.itertuples(index=False)]
    return "\n".join([cabecalho, separador, *corpo])
