"""
Punto de entrada principal de la aplicación.
YouTube MP3 Downloader con arquitectura modular.
"""
import sys
import os

# Agregar el directorio src al path para importaciones
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow


def main():
    """Función principal de la aplicación."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
