"""Cliente de linha de comando. Repare que ele só conhece a fachada."""

import argparse
import logging

from clima import PipelineClima


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de clima (versão com Facade)")
    parser.add_argument("--cidades", nargs="+", default=["Rio de Janeiro", "São Paulo", "Belo Horizonte"])
    parser.add_argument("--inicio", default="2026-01-01")
    parser.add_argument("--fim", default="2026-03-31")
    parser.add_argument("--csv", help="Rodar offline lendo este CSV em vez da API")
    parser.add_argument("--saida", default="saida")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    pipeline = PipelineClima.offline(args.csv, args.saida) if args.csv else PipelineClima(pasta_saida=args.saida)
    resultado = pipeline.executar(args.cidades, args.inicio, args.fim)
    print(resultado.mensal.to_string(index=False))


if __name__ == "__main__":
    main()
