"""Pipeline de dados climáticos organizado com o padrão Facade.

O cliente só precisa importar `PipelineClima`. Os subsistemas continuam
acessíveis para quem precisar de controle fino.
"""

from .facade import PipelineClima, ResultadoPipeline

__all__ = ["PipelineClima", "ResultadoPipeline"]
