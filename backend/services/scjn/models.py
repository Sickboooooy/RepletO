"""
📋 Data Models for SCJN Integration
"""

from typing import TypedDict, Optional, List, Literal
from datetime import datetime


class VigenciaInfo(TypedDict):
    """Información de vigencia de tesis"""
    status: Literal['vigente', 'contradiccion', 'superada']
    fecha_validacion: datetime
    notas: Optional[str]


class FichaTecnica(TypedDict):
    """Ficha técnica de una tesis"""
    registro: str  # ej: "1a./J. 45/2023"
    ponente: str
    fecha: datetime
    instancia: str  # "Primera Sala", "Segunda Sala", "Pleno"
    materia: str  # "Laboral", "Penal", "Civil", etc
    tipo: str  # "Jurisprudencia", "Tesis Aislada"


class TesisResult(TypedDict):
    """Resultado de una tesis SCJN"""
    id: str
    titulo: str
    registro: str
    materia: str
    sala: str
    year: int
    contenido: str
    ficha_tecnica: FichaTecnica
    vigencia: VigenciaInfo
    url: str
    download_url: Optional[str]
    extracted_at: datetime
    source: Literal['scjn', 'cache']


class SearchFilters(TypedDict, total=False):
    """Filtros disponibles para búsqueda en SCJN"""
    materia: str  # Civil, Penal, Laboral, Fiscal, etc
    sala: str  # Primera, Segunda, Pleno
    year: int
    tipo: str  # Jurisprudencia, Tesis Aislada
    instancia: str
    ponente: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]


class SearchResponse(TypedDict):
    """Respuesta de búsqueda"""
    status: Literal['success', 'partial', 'error']
    query: str
    results: List[TesisResult]
    total: int
    execution_time: float
    source: Literal['live', 'cache', 'hybrid']
    cached_results: int
    fresh_results: int


class CrawlJob(TypedDict):
    """Job de sincronización semanal"""
    id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: Literal['pending', 'running', 'completed', 'error']
    tesis_downloaded: int
    tesis_vectorized: int
    errors: List[str]
