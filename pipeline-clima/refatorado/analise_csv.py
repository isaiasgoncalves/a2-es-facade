"""Cliente 2: análise offline de um CSV recebido de outra fonte."""

from pathlib import Path

from clima import PipelineClima

CSV_PADRAO = Path(__file__).resolve().parents[1] / "dados" / "clima_sujo.csv"


def rodar(csv, cidades, inicio, fim, pasta_saida="saida"):
    resultado = PipelineClima.offline(csv, pasta_saida).executar(cidades, inicio, fim)
    print(resultado.validacao)
    return resultado.mensal


if __name__ == "__main__":
    mensal = rodar(CSV_PADRAO, ["Rio de Janeiro", "São Paulo", "Belo Horizonte"], "2026-01-01", "2026-03-31")
    print(mensal.to_string(index=False))
