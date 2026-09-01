"""
Utilidades para manejo de imágenes.
Funciones para procesar y cargar imágenes en la interfaz.
"""
import os
# pyrefly: ignore [missing-import]
from PIL import Image, ImageDraw
from typing import Optional


class ImageUtils:
    """Clase utilitaria para operaciones con imágenes."""

    @staticmethod
    def load_circular_logo(image_path: str, size: tuple[int, int] = (150, 150)) -> Optional[Image.Image]:
        """
        Carga una imagen y la convierte en circular.

        Args:
            image_path: Ruta de la imagen
            size: Tamaño deseado (ancho, alto)

        Returns:
            Imagen procesada o None si hay error
        """
        try:
            if not os.path.exists(image_path):
                return None

            # Cargar y redimensionar imagen
            image = Image.open(image_path)
            image = image.resize(size, Image.Resampling.LANCZOS)

            # Crear máscara circular
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)

            # Aplicar máscara
            image.putalpha(mask)

            return image

        except Exception:
            return None

    @staticmethod
    def load_icon(icon_path: str, size: tuple[int, int] = (32, 32)) -> Optional[Image.Image]:
        """
        Carga un icono y lo redimensiona.

        Args:
            icon_path: Ruta del icono
            size: Tamaño deseado (ancho, alto)

        Returns:
            Imagen redimensionada o None si hay error
        """
        try:
            if not os.path.exists(icon_path):
                return None

            image = Image.open(icon_path)
            return image.resize(size, Image.Resampling.LANCZOS)

        except Exception:
            return None
