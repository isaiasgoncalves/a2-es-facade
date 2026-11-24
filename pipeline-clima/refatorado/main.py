"""Cliente de linha de comando. Repare que ele só conhece a fachada."""

from clima import PipelineClima


def main() -> None:
    CIDADES = ["Rio de Janeiro", "São Paulo", "Belo Horizonte"]
    
    pipeline = PipelineClima(pasta_saida="../saida")
    resultado = pipeline.executar(CIDADES, "2026-01-01", "2026-03-31")
    print(resultado.mensal)

    pipeline_csv = PipelineClima.offline("pipeline-clima/dados/clima_sujo.csv", pasta_saida="../saida")
    resultado_csv = pipeline_csv.executar(CIDADES, "2026-01-01", "2026-03-31")
    print(resultado_csv.validacao)
    print(resultado_csv.mensal)

if __name__ == "__main__":
    main()
