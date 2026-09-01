"""
Servicio de reproducción de audio.
Maneja la reproducción de archivos MP3 usando pygame-ce.
"""
# pyrefly: ignore [missing-import]
import pygame
import threading
import os
from typing import Optional
# pyrefly: ignore [missing-import]
from mutagen.mp3 import MP3


class AudioPlayerService:
    """Servicio que maneja la reproducción de audio."""

    def __init__(self):
        pygame.mixer.init()
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.duration = 0.0  # Duración total del archivo en segundos
        self.start_offset = 0.0  # Posición inicial en segundos desde la que se inició la reproducción
        self.pause_position = 0.0  # Posición exacta al pausar

    def load_file(self, file_path: str) -> bool:
        """Carga un archivo de audio."""
        try:
            if not os.path.exists(file_path):
                return False

            # Liberar cualquier archivo cargado previamente
            self.stop()

            pygame.mixer.music.load(file_path)
            self.current_file = file_path
            self.start_offset = 0.0
            self.pause_position = 0.0
            pygame.mixer.music.set_volume(self.volume)

            # Obtener duración del archivo
            try:
                audio = MP3(file_path)
                self.duration = audio.info.length
            except:
                self.duration = 0.0

            return True
        except Exception as e:
            print(f"Error cargando archivo: {e}")
            return False

    def play(self, start_time: float = 0.0) -> bool:
        """Reproduce el audio cargado especificando opcionalmente el tiempo inicial."""
        try:
            if self.current_file:
                self.start_offset = max(0.0, min(self.duration, start_time)) if self.duration > 0 else max(0.0, start_time)
                self.pause_position = self.start_offset
                pygame.mixer.music.play(start=self.start_offset)
                self.is_playing = True
                self.is_paused = False
                return True
            return False
        except Exception as e:
            print(f"Error reproduciendo: {e}")
            return False

    def pause(self):
        """Pausa la reproducción guardando la posición exacta."""
        if not self.is_paused:
            self.pause_position = self.get_position()  # Guardar segundos exactos
            pygame.mixer.music.pause()
            self.is_paused = True

    def resume(self):
        """Reanuda desde donde se pausó sin reiniciar a 0:00."""
        if self.is_paused:
            # CRÍTICO: restaurar start_offset con la posición de pausa
            # porque después de unpause(), get_pos() vuelve a contar desde 0ms
            # y get_position() calcula: start_offset + get_pos() = pause_position + 0 = correcto
            self.start_offset = self.pause_position
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True

    def stop(self):
        """Detiene la reproducción y libera el archivo."""
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # Liberar handle de archivo en Windows
        except Exception:
            pass
        self.is_playing = False
        self.is_paused = False
        self.start_offset = 0.0
        self.pause_position = 0.0

    def set_volume(self, volume: float):
        """Establece el volumen (0.0 a 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def get_volume(self) -> float:
        """Obtiene el volumen actual."""
        return self.volume

    def is_audio_playing(self) -> bool:
        """Verifica si el audio está reproduciéndose."""
        return pygame.mixer.music.get_busy() and not self.is_paused

    def get_position(self) -> float:
        """Obtiene la posición actual en segundos."""
        try:
            if self.is_paused:
                return self.pause_position
            if not self.is_playing:
                return 0.0
            elapsed = pygame.mixer.music.get_pos() / 1000.0
            if elapsed < 0:
                elapsed = 0.0
            pos = self.start_offset + elapsed
            return min(self.duration, pos) if self.duration > 0 else pos
        except:
            return self.pause_position if self.is_paused else self.start_offset

    def get_progress(self) -> float:
        """Obtiene el progreso actual como fracción (0.0 a 1.0)."""
        if self.duration <= 0:
            return 0.0
        position = self.get_position()
        return min(1.0, max(0.0, position / self.duration))

    def get_duration(self) -> float:
        """Obtiene la duración total del archivo en segundos."""
        return self.duration

    def seek(self, seconds: float):
        """Establece la posición de reproducción en segundos reiniciando el playback desde target."""
        try:
            if self.current_file:
                target = max(0.0, min(self.duration, seconds)) if self.duration > 0 else max(0.0, seconds)
                self.start_offset = target
                self.pause_position = target
                pygame.mixer.music.play(start=target)
                self.is_playing = True
                self.is_paused = False
        except Exception as e:
            print(f"Error en seek: {e}")

    def cleanup(self):
        """Limpia recursos."""
        pygame.mixer.quit()
