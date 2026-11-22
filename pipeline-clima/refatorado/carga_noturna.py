"""Cliente 3: carga noturna no banco, sem relatório."""

from clima import PipelineClima


def rodar(cidades, inicio, fim, pasta_saida="saida", fonte=None):
    return PipelineClima(fonte=fonte, pasta_saida=pasta_saida).carregar(cidades, inicio, fim).mensal


if __name__ == "__main__":
    mensal = rodar(["Rio de Janeiro", "São Paulo", "Belo Horizonte"], "2026-01-01", "2026-03-31")
    print(mensal.to_string(index=False))
