"""
Interfaz gráfica principal de la aplicación.
Maneja la presentación y la interacción con el usuario.
"""
import os
import re
import customtkinter as ctk
import threading
from typing import Optional
from functools import partial
# pyrefly: ignore [missing-import]
from PIL import Image
from ctkfontawesome import icon_to_ctkimage

from src.config.config import AppConfig
from src.services.download_service import DownloadService
from src.services.search_service import SearchService
from src.services.audio_player_service import AudioPlayerService
from src.models.download_models import DownloadRequest, DownloadProgress, DownloadStatus
from src.models.search_models import SearchResult, SearchRequest
from src.utils.image_utils import ImageUtils


class MainWindow:
    """Ventana principal de la aplicación."""

    def __init__(self):
        self.download_service = DownloadService()
        self.search_service = SearchService()
        self.audio_player = AudioPlayerService()
        self.is_downloading = False
        self.last_log_message = ""  # Para evitar repeticiones en el log
        self.updating_progress_line = False  # Para saber si estamos actualizando una línea de progreso
        self.search_results = []  # Almacenar resultados de búsqueda
        self.selected_video_url = None  # URL del video seleccionado
        self.downloaded_file_path = None  # Ruta del archivo descargado para reproducir
        self.preview_file_path = None  # Ruta del archivo de previsualización
        self.previewing_result_index = None  # Índice del resultado que se está previsualizando
        self.preview_buttons = {}  # Diccionario para guardar referencias a los botones de previsualización
        self.current_song_title = None  # Título de la canción actual en reproducción
        self.current_song_artist = None  # Artista de la canción actual en reproducción
        self.progress_update_running = False  # Control de actualización de progreso
        self.icon_cache = {}  # Caché para iconos reutilizables

        # Configurar apariencia
        ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
        ctk.set_default_color_theme(AppConfig.COLOR_THEME)

        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.root.minsize(AppConfig.MIN_WINDOW_WIDTH, AppConfig.MIN_WINDOW_HEIGHT)

        # Establecer icono
        self._set_window_icon()

        # Configurar ruta base para recursos (PyInstaller)
        if getattr(sys, 'frozen', False):
            AppConfig.set_base_path(sys._MEIPASS)

        # Construir UI
        self._setup_ui()

    def _get_icon(self, name: str, fill: str, scale_to_width: int):
        """Obtiene un icono del caché o crea uno nuevo."""
        cache_key = f"{name}_{fill}_{scale_to_width}"
        if cache_key not in self.icon_cache:
            self.icon_cache[cache_key] = icon_to_ctkimage(name, fill=fill, scale_to_width=scale_to_width)
        return self.icon_cache[cache_key]

    def _set_window_icon(self):
        """Establece el icono de la ventana."""
        try:
            icon_path = AppConfig.get_icon_path()
            if os.path.exists(icon_path):
                self.root.wm_iconbitmap(icon_path)
        except Exception:
            pass

    def _setup_ui(self):
        """Construye la interfaz de usuario."""
        # Frame principal con grid system responsive
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Configurar pesos de filas y columnas para redimensionamiento dinámico
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=0)  # Logo (fijo)
        self.frame.grid_rowconfigure(1, weight=0)  # Búsqueda label (fijo)
        self.frame.grid_rowconfigure(2, weight=0)  # Búsqueda frame (fijo)
        self.frame.grid_rowconfigure(3, weight=1)  # Resultados label (dinámico)
        self.frame.grid_rowconfigure(4, weight=1)  # Resultados lista (dinámico)
        self.frame.grid_rowconfigure(5, weight=0)  # Dir label (fijo)
        self.frame.grid_rowconfigure(6, weight=0)  # Dir frame (fijo)
        self.frame.grid_rowconfigure(7, weight=0)  # Botón descarga (fijo)
        self.frame.grid_rowconfigure(8, weight=0)  # (eliminado controles reproducción)
        self.frame.grid_rowconfigure(9, weight=0)  # Progress bar descarga (fijo)
        self.frame.grid_rowconfigure(10, weight=0)  # Status (fijo)
        self.frame.grid_rowconfigure(11, weight=1)  # Log (menos expansible)

        # Agregar componentes
        self._add_logo()
        self._add_search_input()
        self._add_search_results()
        self._add_directory_input()
        self._add_download_button()
        self._add_audio_controls()
        self._add_player_mode()
        self._add_progress_bar()
        self._add_status_label()
        self._add_log_area()

    def _add_logo(self):
        """Agrega el logo redondo."""
        try:
            logo_path = AppConfig.get_logo_path()
            logo_image = ImageUtils.load_circular_logo(logo_path, (180, 180))

            if logo_image:
                logo_ctk = ctk.CTkImage(logo_image, size=(180, 180))
                self.logo_label = ctk.CTkLabel(self.frame, image=logo_ctk, text="")
                self.logo_label.grid(row=0, column=0, pady=(5, 5))
            else:
                # Crear label vacío si no hay logo
                self.logo_label = ctk.CTkLabel(self.frame, text="Dow-Music", font=("Arial", 20, "bold"))
                self.logo_label.grid(row=0, column=0, pady=(5, 5))
        except Exception:
            # Crear label de texto como fallback
            self.logo_label = ctk.CTkLabel(self.frame, text="Dow-Music", font=("Arial", 20, "bold"))
            self.logo_label.grid(row=0, column=0, pady=(5, 5))

    def _add_search_input(self):
        """Agrega el campo de búsqueda de videos."""
        self.search_label = ctk.CTkLabel(self.frame, text="Buscar videos en YouTube:")
        self.search_label.grid(row=1, column=0, pady=(10, 5), sticky="w", padx=20)

        self.search_frame = ctk.CTkFrame(self.frame)
        self.search_frame.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Nombre de canción o video..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        # Agregar evento para limpiar URL cuando se escribe en búsqueda
        self.search_entry.bind("<KeyRelease>", self._on_search_input)

        search_icon = self._get_icon("magnifying-glass", "#ffffff", 18)
        self.search_button = ctk.CTkButton(
            self.search_frame,
            text="Buscar",
            image=search_icon,
            compound="left",
            command=self._search_videos,
            width=80
        )
        self.search_button.grid(row=0, column=1)

    def _add_search_results(self):
        """Agrega el área para mostrar resultados de búsqueda."""
        self.results_label = ctk.CTkLabel(self.frame, text="Resultados de búsqueda:")
        self.results_label.grid(row=3, column=0, pady=(10, 5), sticky="w", padx=20)
        self.results_label.grid_remove()  # Oculto inicialmente

        # Frame para resultados (inicialmente oculto en fila 4)
        self.results_frame = ctk.CTkFrame(self.frame)
        self.results_frame.grid(row=4, column=0, pady=(0, 10), padx=20, sticky="nsew")
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_remove()  # Oculto inicialmente

        # Scrollable frame para resultados (sin height fijo para mejor adaptación)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.results_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Variable para el radiobutton seleccionado
        self.selected_result_var = ctk.StringVar(value="")

        # Botón para cerrar resultados
        close_icon = self._get_icon("xmark", "#ffffff", 16)
        self.close_results_button = ctk.CTkButton(
            self.results_frame,
            text="Cerrar",
            image=close_icon,
            compound="left",
            command=self._close_search_results,
            height=30
        )
        self.close_results_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

    def _add_directory_input(self):
        """Agrega el campo de selección de directorio."""
        self.dir_label = ctk.CTkLabel(self.frame, text="Directorio de Descarga:")
        self.dir_label.grid(row=5, column=0, pady=(10, 5), sticky="w", padx=20)

        self.dir_frame = ctk.CTkFrame(self.frame)
        self.dir_frame.grid(row=6, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.dir_frame.grid_columnconfigure(0, weight=1)

        self.dir_entry = ctk.CTkEntry(self.dir_frame)
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.dir_entry.insert(0, AppConfig.DEFAULT_DOWNLOAD_DIR)

        folder_icon = self._get_icon("folder-open", "#ffffff", 18)
        self.browse_button = ctk.CTkButton(
            self.dir_frame,
            text="Examinar",
            image=folder_icon,
            compound="left",
            command=self._browse_directory,
            width=80
        )
        self.browse_button.grid(row=0, column=1)

    def _add_download_button(self):
        """Agrega el botón de descarga."""
        download_main_icon = self._get_icon("download", "#ffffff", 24)
        self.download_button = ctk.CTkButton(
            self.frame,
            text="Descargar MP3",
            image=download_main_icon,
            compound="left",
            command=self._start_download,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.download_button.grid(row=7, column=0, pady=20, padx=20, sticky="ew")

    def _add_audio_controls(self):
        """Este método ya no se usa, los controles están en el modo reproductor."""
        pass

    def _add_player_mode(self):
        """Agrega el modo reproductor profesional e intuitivo."""
        self.player_frame = ctk.CTkFrame(self.frame, fg_color="#0f0f1a")
        self.player_frame.grid(row=0, column=0, rowspan=12, pady=0, padx=0, sticky="nsew")
        self.player_frame.grid_remove()  # Ocultar al inicio
        self.player_frame.grid_columnconfigure(0, weight=1)

        # Logo centrado
        try:
            logo_path = AppConfig.get_logo_path()
            logo_image = ImageUtils.load_circular_logo(logo_path, (120, 120))
            if logo_image:
                logo_ctk = ctk.CTkImage(logo_image, size=(120, 120))
                self.player_logo_label = ctk.CTkLabel(self.player_frame, image=logo_ctk, text="")
            else:
                self.player_logo_label = ctk.CTkLabel(self.player_frame, text="🎵", font=("Arial", 60))
        except Exception:
            self.player_logo_label = ctk.CTkLabel(self.player_frame, text="🎵", font=("Arial", 60))
        self.player_logo_label.pack(pady=(15, 5))

        # Tarjeta de Información de Canción
        self.song_info_frame = ctk.CTkFrame(self.player_frame, fg_color="#1a1a2e", corner_radius=16)
        self.song_info_frame.pack(fill="x", padx=25, pady=8)

        self.song_title_label = ctk.CTkLabel(
            self.song_info_frame,
            text="Título de la Canción",
            font=("Helvetica", 18, "bold"),
            text_color="#ffffff",
            wraplength=340,
            anchor="center"
        )
        self.song_title_label.pack(pady=(12, 2), padx=15)

        self.song_artist_label = ctk.CTkLabel(
            self.song_info_frame,
            text="Artista",
            font=("Helvetica", 13),
            text_color="#00d4ff",
            anchor="center"
        )
        self.song_artist_label.pack(pady=(0, 10), padx=15)

        # Fila de Línea de Tiempo: [00:00] [Barra de Progreso] [03:45]
        self.timeline_frame = ctk.CTkFrame(self.song_info_frame, fg_color="transparent")
        self.timeline_frame.pack(fill="x", padx=15, pady=(0, 12))
        self.timeline_frame.grid_columnconfigure(1, weight=1)

        self.time_current_label = ctk.CTkLabel(
            self.timeline_frame,
            text="00:00",
            font=("Consolas", 11, "bold"),
            text_color="#a0a0b0"
        )
        self.time_current_label.grid(row=0, column=0, padx=(0, 8))

        self.visual_progress_bar = ctk.CTkProgressBar(
            self.timeline_frame,
            progress_color="#00d4ff",
            corner_radius=4,
            height=8
        )
        self.visual_progress_bar.grid(row=0, column=1, sticky="ew")
        self.visual_progress_bar.set(0.0)

        self.time_total_label = ctk.CTkLabel(
            self.timeline_frame,
            text="00:00",
            font=("Consolas", 11, "bold"),
            text_color="#a0a0b0"
        )
        self.time_total_label.grid(row=0, column=2, padx=(8, 0))

        # Controles Principales de Reproducción Intuitivos
        self.player_controls_frame = ctk.CTkFrame(self.player_frame, fg_color="#1a1a2e", corner_radius=18)
        self.player_controls_frame.pack(fill="x", padx=25, pady=8)
        for i in range(3):
            self.player_controls_frame.grid_columnconfigure(i, weight=1)

        # Botón Retroceder 10s
        skip_back_icon = self._get_icon("backward-step", "#ffffff", 20)
        self.skip_back_button = ctk.CTkButton(
            self.player_controls_frame,
            text="-10s",
            font=("Helvetica", 11, "bold"),
            image=skip_back_icon,
            compound="left",
            width=65,
            height=42,
            fg_color="#2a2a3e",
            hover_color="#3a3a4e",
            text_color="#ffffff",
            corner_radius=14,
            command=self._skip_backward
        )
        self.skip_back_button.grid(row=0, column=0, pady=10, padx=4)

        # Botón Central Principal Play / Pause Toggle
        play_icon = self._get_icon("play", "#ffffff", 32)
        self.player_main_play_button = ctk.CTkButton(
            self.player_controls_frame,
            text="",
            image=play_icon,
            width=68,
            height=68,
            fg_color="#2a2a3e",
            hover_color="#3a3a4e",
            text_color="#ffffff",
            corner_radius=34,
            command=self._toggle_play_pause
        )
        self.player_main_play_button.grid(row=0, column=1, pady=8, padx=4)

        # Botón Adelantar 10s
        skip_forward_icon = self._get_icon("forward-step", "#ffffff", 20)
        self.skip_forward_button = ctk.CTkButton(
            self.player_controls_frame,
            text="+10s",
            font=("Helvetica", 11, "bold"),
            image=skip_forward_icon,
            compound="right",
            width=65,
            height=42,
            fg_color="#2a2a3e",
            hover_color="#3a3a4e",
            text_color="#ffffff",
            corner_radius=14,
            command=self._skip_forward
        )
        self.skip_forward_button.grid(row=0, column=2, pady=10, padx=4)



        # Control de Volumen Interactivo (🔊)
        self.volume_frame = ctk.CTkFrame(self.player_frame, fg_color="#1a1a2e", corner_radius=14)
        self.volume_frame.pack(fill="x", padx=25, pady=5)
        self.volume_frame.grid_columnconfigure(1, weight=1)

        vol_icon = self._get_icon("volume-high", "#00d4ff", 20)
        self.vol_icon_label = ctk.CTkLabel(
            self.volume_frame,
            image=vol_icon,
            text=""
        )
        self.vol_icon_label.grid(row=0, column=0, padx=(12, 4), pady=6)

        self.volume_slider = ctk.CTkSlider(
            self.volume_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            progress_color="#00d4ff",
            button_color="#00d4ff",
            button_hover_color="#00e5ff",
            command=self._on_player_volume_change
        )
        self.volume_slider.grid(row=0, column=1, sticky="ew", padx=(4, 12), pady=6)
        self.volume_slider.set(0.7)

        # Etiqueta de Notificación en Tiempo Real (Toast)
        self.player_notice_label = ctk.CTkLabel(
            self.player_frame,
            text="",
            font=("Helvetica", 12, "bold"),
            text_color="#00ff88"
        )
        self.player_notice_label.pack(pady=(0, 5))

        # Botones de Acción Inmediata
        self.action_frame = ctk.CTkFrame(self.player_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=25, pady=(5, 15))
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        download_icon = self._get_icon("download", "#0f0f1a", 20)
        self.quick_download_button = ctk.CTkButton(
            self.action_frame,
            text="Descargar MP3",
            font=("Helvetica", 13, "bold"),
            image=download_icon,
            compound="left",
            height=38,
            fg_color="#00d4ff",
            hover_color="#00e5ff",
            text_color="#0f0f1a",
            corner_radius=19,
            command=self._download_from_player
        )
        self.quick_download_button.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        back_icon = self._get_icon("arrow-left", "#ffffff", 20)
        self.back_button = ctk.CTkButton(
            self.action_frame,
            text="Volver",
            font=("Helvetica", 13, "bold"),
            image=back_icon,
            compound="left",
            height=38,
            fg_color="#1a1a2e",
            hover_color="#2a2a3e",
            text_color="#ffffff",
            corner_radius=19,
            command=self._exit_player_mode
        )
        self.back_button.grid(row=0, column=1, padx=(4, 0), sticky="ew")

    def _add_progress_bar(self):
        """Agrega la barra de progreso con diseño mejorado."""
        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            progress_color="#00d4ff",
            corner_radius=3,
            height=8
        )
        self.progress_bar.grid(row=9, column=0, pady=(10, 5), padx=20, sticky="ew")
        self.progress_bar.set(0)

    def _add_status_label(self):
        """Agrega la etiqueta de estado."""
        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Listo para descargar",
            text_color="gray"
        )
        self.status_label.grid(row=10, column=0, pady=(5, 20), sticky="ew", padx=20)

    def _add_log_area(self):
        """Agrega el área de log."""
        self.log_text = ctk.CTkTextbox(self.frame, wrap="word")
        self.log_text.grid(row=11, column=0, pady=(0, 20), padx=20, sticky="nsew")
        self.log_text.configure(state="disabled", font=("Consolas", 9))

    def _browse_directory(self):
        """Abre el diálogo para seleccionar directorio."""
        from tkinter import filedialog
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def _enter_player_mode(self, song_title: str, song_artist: str = None):
        """Entra al modo reproductor profesional."""
        self.current_song_title = song_title
        self.current_song_artist = song_artist or "Desconocido"

        # Actualizar información de la canción
        self.song_title_label.configure(text=song_title)
        self.song_artist_label.configure(text=self.current_song_artist)

        # Ocultar TODOS los elementos de la vista normal (incluyendo logo original)
        self.logo_label.grid_remove()
        self.search_label.grid_remove()
        self.search_frame.grid_remove()
        self.dir_label.grid_remove()
        self.dir_frame.grid_remove()
        self.download_button.grid_remove()
        self.progress_bar.grid_remove()
        self.status_label.grid_remove()
        self.log_text.grid_remove()
        self.results_frame.grid_remove()
        self.results_label.grid_remove()

        # Mostrar modo reproductor (que tiene su propio logo)
        self.player_frame.grid()

        # Iniciar actualización de barra de progreso
        self._start_progress_update()

        self._log(f"Entrando al modo reproductor: {song_title}")

    def _exit_player_mode(self):
        """Sale del modo reproductor y vuelve a la vista normal."""
        # Detener actualización de barra de progreso
        self._stop_progress_update()

        # Detener la reproducción de previsualización pero NO limpiar el archivo temporal
        if self.previewing_result_index is not None:
            self.audio_player.stop()
            # NO limpiar el archivo temporal, mantenerlo para reutilización
            # Solo actualizar el botón a estado de pausa
            self._update_preview_button(self.previewing_result_index, "▶")

        # Ocultar modo reproductor
        self.player_frame.grid_remove()

        # Restaurar logo
        self.logo_label.grid(row=0, column=0, pady=(5, 5))

        # Si había resultados de búsqueda, restaurar solo logo, resultados y log
        if self.search_results:
            self.results_frame.grid()
            self.results_label.grid()
            self.log_text.grid(row=11, column=0, pady=(0, 20), padx=20, sticky="nsew")
        else:
            # Si no hay resultados, restaurar vista normal completa
            self.search_label.grid(row=1, column=0, pady=(10, 5), sticky="w", padx=20)
            self.search_frame.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="ew")
            self.dir_label.grid(row=5, column=0, pady=(10, 5), sticky="w", padx=20)
            self.dir_frame.grid(row=6, column=0, pady=(0, 10), padx=20, sticky="ew")
            self.download_button.grid(row=7, column=0, pady=20, padx=20, sticky="ew")
            self.progress_bar.grid(row=9, column=0, pady=(10, 5), padx=20, sticky="ew")
            self.status_label.grid(row=10, column=0, pady=(5, 20), sticky="ew", padx=20)
            self.log_text.grid(row=11, column=0, pady=(0, 20), padx=20, sticky="nsew")

        self._log("Saliendo del modo reproductor (archivo temporal mantenido)")

    def _format_time_sec(self, seconds: float) -> str:
        """Formatea segundos en formato MM:SS."""
        if not seconds or seconds < 0:
            return "00:00"
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m:02d}:{s:02d}"

    def _toggle_play_pause(self):
        """Alterna entre reproducción y pausa con un solo botón central."""
        try:
            if self.audio_player.is_audio_playing():
                self.audio_player.pause()
                play_icon = self._get_icon("play", "#ffffff", 32)
                self.player_main_play_button.configure(image=play_icon, fg_color="#00d4ff")
                self._update_status("Previsualización pausada", "orange")
            else:
                if self.audio_player.is_paused:
                    self.audio_player.resume()
                elif self.preview_file_path and os.path.exists(self.preview_file_path):
                    self.audio_player.load_file(self.preview_file_path)
                    self.audio_player.play()
                pause_icon = self._get_icon("pause", "#ffffff", 32)
                self.player_main_play_button.configure(image=pause_icon, fg_color="#2a2a3e")
                self._update_status("Reproduciendo previsualización...", "green")
        except Exception as e:
            self._log(f"Error al reproducir/pausar: {str(e)}")

    def _skip_backward(self):
        """Retrocede 10 segundos."""
        try:
            curr = self.audio_player.get_position()
            self.audio_player.seek(max(0.0, curr - 10.0))
        except Exception:
            pass

    def _skip_forward(self):
        """Adelanta 10 segundos."""
        try:
            curr = self.audio_player.get_position()
            dur = self.audio_player.get_duration()
            self.audio_player.seek(min(dur, curr + 10.0))
        except Exception:
            pass

    def _on_player_volume_change(self, value):
        """Ajusta el volumen en tiempo real."""
        self.audio_player.set_volume(value)

    def _download_from_player(self):
        """Inicia la descarga desde el modo reproductor con verificación de duplicados."""
        if self.is_downloading:
            self.player_notice_label.configure(
                text="Descarga ya en curso",
                text_color="#ffcc00"
            )
            self.root.after(3000, lambda: self.player_notice_label.configure(text=""))
            return

        # Verificar si hay URL seleccionada
        if not self.selected_video_url:
            self.player_notice_label.configure(
                text="No hay video seleccionado",
                text_color="#ff4444"
            )
            self.root.after(3000, lambda: self.player_notice_label.configure(text=""))
            return

        # Obtener directorio de salida
        output_dir = self.dir_entry.get()
        if not output_dir:
            self.player_notice_label.configure(
                text="Directorio no configurado",
                text_color="#ff4444"
            )
            self.root.after(3000, lambda: self.player_notice_label.configure(text=""))
            return

        # Verificar si el archivo ya existe
        is_duplicate, existing_path = self.download_service.check_duplicate(
            self.selected_video_url, output_dir, AppConfig.AUDIO_FORMAT
        )
        if is_duplicate:
            self.player_notice_label.configure(
                text="Este audio ya fue descargado",
                text_color="#00ff88"
            )
            self.root.after(4000, lambda: self.player_notice_label.configure(text=""))
            self._log(f"El archivo ya existe: {existing_path}")
            return

        # Iniciar descarga
        self.is_downloading = True
        loading_icon = self._get_icon("spinner", "#ffffff", 20)
        self.quick_download_button.configure(
            state="disabled",
            text="Descargando...",
            image=loading_icon,
            fg_color="#666666",
            hover_color="#666666"
        )

        # Crear solicitud de descarga
        request = DownloadRequest(
            url=self.selected_video_url,
            output_dir=output_dir,
            quality=AppConfig.AUDIO_QUALITY,
            format=AppConfig.AUDIO_FORMAT
        )

        # Iniciar descarga en hilo separado
        thread = threading.Thread(
            target=self._download_thread_from_player,
            args=(request,)
        )
        thread.daemon = True
        thread.start()

        # Mostrar notificación
        self.player_notice_label.configure(
            text="Descarga iniciada...",
            text_color="#00ff88"
        )

    def _download_thread_from_player(self, request: DownloadRequest):
        """Hilo que ejecuta la descarga desde el reproductor."""
        def progress_callback(progress: DownloadProgress):
            """Callback para actualizar progreso en el hilo principal."""
            self.root.after(0, partial(self._update_progress, progress))

        try:
            result = self.download_service.download_audio(request, progress_callback)
            
            # Actualizar UI en el hilo principal
            if result.success:
                self.root.after(0, partial(self._handle_download_success_from_player, result))
            else:
                self.root.after(0, partial(self._handle_download_error_from_player, result))
        except Exception as e:
            self.root.after(0, partial(self._handle_download_error_from_player, None, str(e)))

    def _handle_download_success_from_player(self, result):
        """Maneja el éxito de descarga desde el reproductor."""
        self.is_downloading = False
        download_icon = self._get_icon("download", "#0f0f1a", 20)
        self.quick_download_button.configure(
            state="normal",
            text="Descargar MP3",
            image=download_icon,
            fg_color="#00d4ff",
            hover_color="#00e5ff"
        )
        
        self.player_notice_label.configure(
            text="Descarga completada",
            text_color="#00ff88"
        )
        self.root.after(4000, lambda: self.player_notice_label.configure(text=""))
        self._log(f"Descarga completada: {result.output_path}")

    def _handle_download_error_from_player(self, result, error_msg=None):
        """Maneja el error de descarga desde el reproductor."""
        self.is_downloading = False
        download_icon = self._get_icon("download", "#0f0f1a", 20)
        self.quick_download_button.configure(
            state="normal",
            text="Descargar MP3",
            image=download_icon,
            fg_color="#00d4ff",
            hover_color="#00e5ff"
        )
        
        message = error_msg or (result.error_message if result else "Error desconocido")
        self.player_notice_label.configure(
            text=f"Error: {message}",
            text_color="#ff4444"
        )
        self.root.after(4000, lambda: self.player_notice_label.configure(text=""))
        self._log(f"Error en descarga: {message}")

    def _play_audio(self):
        """Reanuda o inicia la reproducción en el modo reproductor."""
        self._toggle_play_pause()

    def _pause_audio(self):
        """Pausa o reanuda la reproducción de previsualización."""
        self._toggle_play_pause()

    def _stop_audio(self):
        """Detiene la reproducción de audio y reinicia la barra sin cerrar el reproductor."""
        try:
            self.audio_player.stop()
            self.visual_progress_bar.set(0.0)
            self.time_current_label.configure(text="00:00")
            if hasattr(self, 'player_main_play_button'):
                play_icon = self._get_icon("play", "#ffffff", 32)
                self.player_main_play_button.configure(image=play_icon, fg_color="#00d4ff")
            self._update_status("Reproducción detenida", "orange")
        except Exception:
            pass

    def _start_progress_update(self):
        """Inicia la actualización periódica de la barra de progreso."""
        if not self.progress_update_running:
            self.progress_update_running = True
            self._update_progress_bar()

    def _stop_progress_update(self):
        """Detiene la actualización de la barra de progreso."""
        self.progress_update_running = False

    def _update_progress_bar(self):
        """Actualiza la barra de progreso y el contador de tiempo del reproductor."""
        if not self.progress_update_running:
            return

        try:
            if self.audio_player.is_audio_playing() or self.audio_player.is_paused:
                progress = self.audio_player.get_progress()
                self.visual_progress_bar.set(progress)

                curr_pos = self.audio_player.get_position()
                dur = self.audio_player.get_duration()

                self.time_current_label.configure(text=self._format_time_sec(curr_pos))
                if dur > 0:
                    self.time_total_label.configure(text=self._format_time_sec(dur))

                # Sincronizar icono del botón central Play/Pause
                if self.audio_player.is_audio_playing():
                    self.player_main_play_button.configure(text="⏸", fg_color="#2a2a3e", text_color="#ffffff")
                else:
                    self.player_main_play_button.configure(text="▶", fg_color="#00d4ff", text_color="#0f0f1a")
        except Exception:
            pass

        if self.progress_update_running:
            self.root.after(100, self._update_progress_bar)

    def _log(self, message: str, update_last: bool = False):
        """Agrega un mensaje al área de log o actualiza la última línea en tiempo real."""
        try:
            self.log_text.configure(state="normal")

            if update_last and self.updating_progress_line:
                # Reemplazar la última línea en lugar de acumular múltiples renglones
                self.log_text.delete("end-1c linestart", "end-1c")
                self.log_text.insert("end-1c", message)
            else:
                if message == self.last_log_message:
                    self.log_text.configure(state="disabled")
                    return

                self.last_log_message = message

                # Asegurar que el nuevo mensaje inicie en una línea limpia
                current_text = self.log_text.get("1.0", "end-1c")
                if current_text and not current_text.endswith("\n"):
                    self.log_text.insert("end-1c", "\n")

                self.log_text.insert("end-1c", message + "\n")

            self.log_text.see("end")  # Auto-scroll al final
            self.log_text.configure(state="disabled")
            self.log_text.update_idletasks()
        except Exception:
            pass

    def _update_status(self, message: str, color: str = "gray"):
        """Actualiza la etiqueta de estado."""
        self.status_label.configure(text=message, text_color=color)

    def _on_search_input(self, event):
        """Maneja entrada en campo de búsqueda."""
        search_query = self.search_entry.get()

        if search_query:
            self._update_status("Modo búsqueda activado", "gray")

    def _clear_search_results(self):
        """Limpia los resultados de búsqueda."""
        self.search_results = []
        self.selected_result_var.set("")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _search_videos(self):
        """Busca videos en YouTube en un hilo separado."""
        query = self.search_entry.get()

        if not query or len(query.strip()) < 2:
            self._log("La búsqueda debe tener al menos 2 caracteres")
            self._update_status("Búsqueda muy corta", "red")
            return

        self._log(f"Buscando: {query}")
        self._update_status("Buscando videos...", "yellow")

        # Ejecutar búsqueda en hilo separado
        thread = threading.Thread(target=self._perform_search, args=(query,))
        thread.daemon = True
        thread.start()

    def _perform_search(self, query: str):
        """Realiza la búsqueda de videos."""
        try:
            request = SearchRequest(query=query, max_results=10)
            success, results, error = self.search_service.search_videos(request)

            # Actualizar UI en el hilo principal usando partial
            self.root.after(0, partial(self._handle_search_results, success, results, error))
        except Exception as e:
            self.root.after(0, partial(self._log, f"Error en búsqueda: {str(e)}"))
            self.root.after(0, partial(self._update_status, "Error en búsqueda", "red"))

    def _handle_search_results(self, success: bool, results: list, error: Optional[str]):
        """Maneja los resultados de búsqueda."""
        if success and results:
            self.search_results = results
            self._display_search_results(results)
            self._show_search_mode()
            self._log(f"Se encontraron {len(results)} resultados")
            self._update_status(f"Se encontraron {len(results)} videos", "green")
        else:
            self._log(f"Error: {error}" if error else "No se encontraron resultados")
            self._update_status("Búsqueda sin resultados", "orange")

    def _show_search_mode(self):
        """Muestra el modo de búsqueda y oculta elementos no necesarios."""
        self._log("Entrando al modo de búsqueda")
        self.results_frame.grid()
        self.results_label.grid()

        # Ajustar weight de filas para mejor distribución en modo búsqueda
        self.frame.grid_rowconfigure(3, weight=0)  # Label resultados (fijo)
        self.frame.grid_rowconfigure(4, weight=1)  # Frame resultados (expansible)

        # Ocultar elementos de descarga pero mantener la barra de progreso
        self.dir_label.grid_remove()
        self.dir_frame.grid_remove()
        self.download_button.grid_remove()
        self.status_label.grid_remove()

        self._log("Elementos ocultados en modo búsqueda")

    def _close_search_results(self):
        """Cierra los resultados de búsqueda y restaura la vista normal."""
        self.results_frame.grid_remove()
        self.results_label.grid_remove()

        # Restaurar weight de filas a configuración normal
        self.frame.grid_rowconfigure(3, weight=0)  # Label resultados (fijo)
        self.frame.grid_rowconfigure(4, weight=0)  # Frame resultados (fijo)

        # Restaurar TODOS los elementos ocultos
        self.logo_label.grid(row=0, column=0, pady=(5, 5))
        self.search_label.grid(row=1, column=0, pady=(10, 5), sticky="w", padx=20)
        self.search_frame.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.dir_label.grid(row=5, column=0, pady=(10, 5), sticky="w", padx=20)
        self.dir_frame.grid(row=6, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.download_button.grid(row=7, column=0, pady=20, padx=20, sticky="ew")
        self.progress_bar.grid(row=9, column=0, pady=(10, 5), padx=20, sticky="ew")
        self.status_label.grid(row=10, column=0, pady=(5, 20), sticky="ew", padx=20)
        self.log_text.grid(row=11, column=0, pady=(0, 20), padx=20, sticky="nsew")

        self._update_status("Video seleccionado - Lista para descargar", "green")

    def _display_search_results(self, results: list):
        """Muestra los resultados de búsqueda con radiobuttons y botones de reproducción."""
        # Limpiar resultados anteriores
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Forzar actualización de UI después de destruir widgets
        self.scrollable_frame.update_idletasks()

        # Limpiar diccionario de botones
        self.preview_buttons = {}

        # Crear radiobuttons para cada resultado
        for i, result in enumerate(results):
            # Frame para cada resultado
            result_frame = ctk.CTkFrame(self.scrollable_frame)
            result_frame.pack(fill="x", padx=5, pady=5)

            # Frame superior con radiobutton y botón de reproducción
            top_frame = ctk.CTkFrame(result_frame)
            top_frame.pack(fill="x", padx=5, pady=2)

            # Radiobutton
            radio = ctk.CTkRadioButton(
                top_frame,
                text=f"{i + 1}. {result.title}",
                variable=self.selected_result_var,
                value=str(i),
                command=lambda r=result: self._on_result_selected(r)
            )
            radio.pack(side="left", padx=5, pady=2)

            # Botón de reproducción para previsualización
            play_preview_icon = self._get_icon("play", "#ffffff", 16)
            preview_button = ctk.CTkButton(
                top_frame,
                text="",
                image=play_preview_icon,
                width=40,
                command=lambda idx=i, res=result: self._preview_audio(idx, res)
            )
            preview_button.pack(side="right", padx=5, pady=2)

            # Guardar referencia al botón
            self.preview_buttons[i] = preview_button

            # Información adicional
            info_text = ""
            if result.duration:
                info_text += f"Duración: {result.duration} | "
            if result.uploader:
                info_text += f"Canal: {result.uploader}"

            if info_text:
                info_label = ctk.CTkLabel(result_frame, text=info_text, font=("Arial", 10))
                info_label.pack(anchor="w", padx=25, pady=0)

    def _preview_audio(self, index: int, result: SearchResult):
        """Previsualiza el audio de un resultado de búsqueda."""
        # Asignar selección automáticamente al previsualizar
        self.selected_video_url = result.url
        self.selected_result_var.set(str(index))

        # Si ya se está previsualizando este audio, pausar/reanudar
        if self.previewing_result_index == index:
            if self.audio_player.is_paused:
                self.audio_player.resume()
                self._log(f"Reanudando previsualización: {result.title}")
                self._update_status("Reproduciendo previsualización...", "green")
                self._update_preview_button(index, "pause")
            elif self.audio_player.is_audio_playing():
                self.audio_player.pause()
                self._log(f"Pausando previsualización: {result.title}")
                self._update_status("Previsualización pausada", "orange")
                self._update_preview_button(index, "play")
            else:
                # El audio se detuvo pero el archivo existe, recargar y reproducir
                if self.preview_file_path and os.path.exists(self.preview_file_path):
                    self._log(f"Recargando audio previsualizado: {result.title}")
                    if self.audio_player.load_file(self.preview_file_path):
                        if self.audio_player.play():
                            self._log(f"Reproduciendo previsualización recargada: {result.title}")
                            self._update_status("Reproduciendo previsualización...", "green")
                            self._update_preview_button(index, "pause")
                            self._enter_player_mode(result.title, result.uploader)
                        else:
                            self._log("Error al reproducir audio recargado")
                            self._update_status("Error reproduciendo", "red")
                            self._update_preview_button(index, "play")
                    else:
                        self._log("Error al cargar audio recargado")
                        self._update_status("Error cargando audio", "red")
                        self._update_preview_button(index, "play")
                else:
                    # El archivo no existe, descargar de nuevo
                    self._log("Archivo temporal no existe, descargando de nuevo")
                    self.previewing_result_index = None
                    self._start_new_preview_download(index, result)
            return

        # Si se está previsualizando otro audio, limpiar su archivo temporal
        if self.previewing_result_index is not None and self.previewing_result_index != index:
            self._cleanup_preview_file()
            self._update_preview_button(self.previewing_result_index, "▶")

        # Iniciar nueva descarga de previsualización
        self._start_new_preview_download(index, result)

    def _start_new_preview_download(self, index: int, result: SearchResult):
        """Inicia una nueva descarga de previsualización."""
        # Detener cualquier reproducción de archivo descargado
        if self.downloaded_file_path and self.audio_player.is_audio_playing():
            self.audio_player.stop()

        # Actualizar botón a estado de descarga
        self._update_preview_button(index, "spinner")

        # Iniciar descarga temporal para previsualización
        self._log(f"Descargando previsualización: {result.title}")
        self._update_status("Descargando previsualización...", "yellow")

        # Crear solicitud de descarga temporal
        import tempfile
        temp_dir = tempfile.gettempdir()

        request = DownloadRequest(
            url=result.url,
            output_dir=temp_dir,
            quality=AppConfig.AUDIO_QUALITY,
            format=AppConfig.AUDIO_FORMAT
        )

        # Iniciar descarga en hilo separado
        thread = threading.Thread(
            target=self._preview_download_thread,
            args=(request, index, result)
        )
        thread.daemon = True
        thread.start()

    def _preview_download_thread(self, request: DownloadRequest, index: int, result: SearchResult):
        """Hilo que ejecuta la descarga de previsualización."""
        self._log(f"Previsualizando: {result.title}")
        self.updating_progress_line = False

        def progress_callback(progress: DownloadProgress):
            """Callback para actualizar progreso en el hilo principal."""
            self.root.after(0, partial(self._update_progress, progress))

        try:
            result_download = self.download_service.download_audio(request, progress_callback)
        except Exception as e:
            result_download = None

        # Actualizar UI en el hilo principal usando partial
        if result_download:
            self.root.after(0, partial(self._handle_preview_result, result_download, index, result))

    def _handle_preview_result(self, result, index: int, search_result: SearchResult):
        """Maneja el resultado de la descarga de previsualización."""
        if result.success:
            self.preview_file_path = result.output_path
            self.previewing_result_index = index

            # Verificar que el archivo existe
            if not os.path.exists(self.preview_file_path):
                self._log("Error: Archivo no encontrado", update_last=self.updating_progress_line)
                self.updating_progress_line = False
                self._update_status("Error: Archivo no encontrado", "red")
                self._update_preview_button(index, "play")
                return

            # Reproducir el audio
            if self.audio_player.load_file(self.preview_file_path):
                if self.audio_player.play():
                    self._log(f"✓ Previsualización lista: {search_result.title}", update_last=self.updating_progress_line)
                    self.updating_progress_line = False
                    self._update_status("Reproduciendo previsualización...", "green")
                    self._update_preview_button(index, "⏸")

                    # Entrar al modo reproductor profesional con la canción en previsualización
                    self._enter_player_mode(search_result.title, search_result.uploader)
                else:
                    self._log("Error al iniciar reproducción", update_last=self.updating_progress_line)
                    self.updating_progress_line = False
                    self._update_status("Error reproduciendo", "red")
                    self._update_preview_button(index, "play")
            else:
                self._log("Error cargando audio", update_last=self.updating_progress_line)
                self.updating_progress_line = False
                self._update_status("Error cargando audio", "red")
                self._update_preview_button(index, "play")
        else:
            self._log(f"Error: {result.error_message}", update_last=self.updating_progress_line)
            self.updating_progress_line = False
            status_msg = result.error_message if result.error_message else "Error en previsualización"
            self._update_status(status_msg, "red")
            self._update_preview_button(index, "play")

    def _cleanup_preview_file(self):
        """Limpia el archivo temporal de previsualización."""
        if self.preview_file_path and os.path.exists(self.preview_file_path):
            try:
                os.remove(self.preview_file_path)
                self._log("Archivo temporal de previsualización eliminado")
            except Exception as e:
                self._log(f"Error eliminando archivo temporal: {e}")
        self.preview_file_path = None
        self.previewing_result_index = None

    def _update_preview_button(self, index: int, icon_name: str):
        """Actualiza el icono del botón de previsualización."""
        if index in self.preview_buttons:
            try:
                icon = self._get_icon(icon_name, "#ffffff", 16)
                self.preview_buttons[index].configure(image=icon, text="")
            except Exception as e:
                self._log(f"Error actualizando botón previsualización: {e}")

    def _on_result_selected(self, result: SearchResult):
        """Maneja la selección de un resultado de búsqueda."""
        self.selected_video_url = result.url
        self._log(f"Video seleccionado: {result.title}")
        self._update_status(f"Seleccionado: {result.title}", "green")

        # Cerrar resultados de búsqueda automáticamente
        self._close_search_results()

    def _select_video_from_search(self):
        """Selecciona un video de los resultados de búsqueda."""
        # Este método ya no se usa, la selección es por radiobutton
        pass

    def _clear_search_results(self):
        """Limpia los resultados de búsqueda."""
        self.search_results = []
        self.selected_result_var.set("")
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _start_download(self):
        """Inicia el proceso de descarga en un hilo separado."""
        if self.is_downloading:
            return

        url = self.selected_video_url
        output_dir = self.dir_entry.get()

        if not url:
            self._log("Error: Debes buscar y seleccionar un video primero")
            self._update_status("Error: Se requiere selección de video", "red")
            return

        if not output_dir:
            self._log("Error: Directorio de salida es requerido")
            self._update_status("Error: Directorio requerido", "red")
            return

        # Verificar si el archivo ya existe en el directorio de destino
        is_duplicate, existing_path = self.download_service.check_duplicate(url, output_dir, AppConfig.AUDIO_FORMAT)
        if is_duplicate:
            self._log(f"El archivo ya existe en el directorio de destino")
            self._log(f"Archivo existente: {existing_path}")
            self._update_status("El archivo ya existe", "orange")
            return

        self.is_downloading = True
        self.download_button.configure(state="disabled", text="Descargando...")
        self.progress_bar.set(0)

        # Crear solicitud de descarga
        request = DownloadRequest(
            url=url,
            output_dir=output_dir,
            quality=AppConfig.AUDIO_QUALITY,
            format=AppConfig.AUDIO_FORMAT
        )

        # Iniciar descarga en hilo separado
        thread = threading.Thread(
            target=self._download_thread,
            args=(request,)
        )
        thread.daemon = True
        thread.start()

    def _download_thread(self, request: DownloadRequest):
        """Hilo que ejecuta la descarga."""
        def progress_callback(progress: DownloadProgress):
            """Callback para actualizar progreso en el hilo principal."""
            self.root.after(0, lambda: self._update_progress(progress))

        result = self.download_service.download_audio(request, progress_callback)

        # Actualizar UI en el hilo principal
        self.root.after(0, lambda: self._handle_download_result(result))

    def _update_progress(self, progress: DownloadProgress):
        """Actualiza la UI con el progreso de descarga en una sola línea dinámica."""
        self.progress_bar.set(progress.progress)
        self._update_status(progress.message, "yellow")

        if progress.status == DownloadStatus.DOWNLOADING or progress.status == DownloadStatus.PROCESSING:
            if not self.updating_progress_line:
                self._log(progress.message)
                self.updating_progress_line = True
            else:
                self._log(message=progress.message, update_last=True)

    def _handle_download_result(self, result):
        """Maneja el resultado de la descarga sustituyendo la línea de progreso."""
        if result.success:
            self._log(f"✓ Descarga completada: {result.video_title}", update_last=self.updating_progress_line)
            self._update_status(f"Descargado: {result.video_title}", "green")
            self.progress_bar.set(1)
            self.downloaded_file_path = result.output_path
        else:
            self._log(f"Error: {result.error_message}", update_last=self.updating_progress_line)
            status_msg = result.error_message if result.error_message else "Error en la descarga"
            self._update_status(status_msg, "red")

        self.updating_progress_line = False
        self.is_downloading = False
        self.download_button.configure(state="normal", text="Descargar MP3")

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


import sys  # Mover import al final para evitar problemas circulares
