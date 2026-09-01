"""
Modelos de datos para la aplicación de descargas.
Define las estructuras de datos utilizadas en la aplicación.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
from datetime import datetime
import re


class DownloadStatus(Enum):
    """Estados posibles de una descarga."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DownloadRequest:
    """Modelo que representa una solicitud de descarga."""
    url: str
    output_dir: str
    quality: str = "192"
    format: str = "mp3"
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida la solicitud de descarga."""
        if not self.url:
            return False, "La URL no puede estar vacía"
        if not self.output_dir:
            return False, "El directorio de salida no puede estar vacío"
        
        # Validar que sea una URL válida
        if not self._is_valid_url(self.url):
            return False, "La URL ingresada no es válida. Por favor ingresa una URL de YouTube válida."
        
        return True, None
    
    def _is_valid_url(self, url: str) -> bool:
        """Valida que la URL tenga un formato correcto."""
        # Patrón para validar URLs (especialmente YouTube)
        pattern = r'^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})|^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        
        if not re.match(pattern, url):
            return False
        
        return True


@dataclass
class DownloadProgress:
    """Modelo que representa el progreso de una descarga."""
    status: DownloadStatus
    progress: float = 0.0  # 0.0 a 1.0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    eta: Optional[float] = None
    message: str = ""
    
    def get_percentage(self) -> float:
        """Retorna el progreso como porcentaje."""
        return self.progress * 100


@dataclass
class DownloadResult:
    """Modelo que representa el resultado de una descarga."""
    success: bool
    video_title: str
    output_path: str
    error_message: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
