"""
Modelos de datos para búsqueda de videos en YouTube.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchResult:
    """Resultado de búsqueda de video de YouTube."""
    video_id: str
    title: str
    url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    view_count: Optional[int] = None
    uploader: Optional[str] = None
    
    def __str__(self):
        return f"{self.title} ({self.duration}) - {self.uploader}"


@dataclass
class SearchRequest:
    """Solicitud de búsqueda de videos."""
    query: str
    max_results: int = 10
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida la solicitud de búsqueda."""
        if not self.query or len(self.query.strip()) < 2:
            return False, "La búsqueda debe tener al menos 2 caracteres"
        return True, None
