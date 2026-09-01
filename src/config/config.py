"""
Módulo de configuración de la aplicación.
Maneja la configuración y constantes de la aplicación.
"""
import os
from pathlib import Path


class AppConfig:
    """Clase que maneja la configuración de la aplicación."""
    
    # Configuración de la ventana
    WINDOW_TITLE = "Dow-Music-Manuel-Dev"
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 700
    MIN_WINDOW_WIDTH = 350
    MIN_WINDOW_HEIGHT = 500
    
    # Configuración de descargas
    DEFAULT_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
    AUDIO_QUALITY = "192"
    AUDIO_FORMAT = "mp3"
    
    # Configuración de UI
    APPEARANCE_MODE = "dark"
    COLOR_THEME = "blue"
    
    # Rutas de recursos
    @staticmethod
    def get_resource_path(filename: str) -> str:
        """Obtiene la ruta completa de un recurso."""
        if hasattr(AppConfig, '_base_path'):
            return os.path.join(AppConfig._base_path, filename)
        return os.path.join(os.path.dirname(__file__), "..", "..", filename)
    
    @staticmethod
    def set_base_path(path: str):
        """Establece la ruta base para recursos (útil para ejecutables PyInstaller)."""
        AppConfig._base_path = path
    
    @staticmethod
    def get_logo_path() -> str:
        """Obtiene la ruta del logo."""
        return AppConfig.get_resource_path("logo.png")
    
    @staticmethod
    def get_icon_path() -> str:
        """Obtiene la ruta del icono."""
        return AppConfig.get_resource_path("icon.ico")
