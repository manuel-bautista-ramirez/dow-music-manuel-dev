"""
Servicio de descarga de videos de YouTube.
Maneja la lógica de negocio para descargar y procesar videos.
"""
import os
import yt_dlp
import imageio_ffmpeg as ffmpeg
from pathlib import Path
from typing import Callable, Optional
from src.models.download_models import (
    DownloadRequest, 
    DownloadProgress, 
    DownloadResult, 
    DownloadStatus
)


class DownloadService:
    """Servicio que maneja las descargas de videos de YouTube."""
    
    def __init__(self):
        self.ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    
    def check_duplicate(self, url: str, output_dir: str, format: str = "mp3") -> tuple[bool, Optional[str]]:
        """
        Verifica si el archivo ya existe en el directorio de destino (case-insensitive).
        Compara solo el nombre base de la canción, ignorando nombre del artista.
        
        Args:
            url: URL del video
            output_dir: Directorio de salida
            format: Formato del archivo (mp3 por defecto)
            
        Returns:
            (es_duplicado, ruta_archivo_existente)
        """
        try:
            # Obtener el nombre base de la canción
            video_title = self._get_video_title(url)
            
            if not video_title or video_title == "Desconocido":
                return False, None
            
            # Normalizar nombre base para comparación (case-insensitive)
            normalized_title = video_title.lower()
            
            # Verificar si el directorio existe
            if not os.path.exists(output_dir):
                return False, None
            
            # Buscar archivos que contengan el nombre de la canción
            files_in_dir = os.listdir(output_dir)
            
            for filename in files_in_dir:
                # Verificar si es el formato correcto
                if filename.lower().endswith(f".{format.lower()}"):
                    # Obtener nombre sin extensión
                    file_name_without_ext = os.path.splitext(filename)[0]
                    
                    # Comparar si el nombre base está contenido en el nombre del archivo
                    # Esto detecta: "Un Beso Al Viento - Los Tinos.mp3" cuando buscamos "Un Beso Al Viento"
                    if normalized_title in file_name_without_ext.lower():
                        # Encontramos coincidencia
                        full_path = os.path.join(output_dir, filename)
                        return True, full_path
            
            return False, None
        except Exception:
            # Si hay error, permitir la descarga
            return False, None
    
    def download_audio(
        self, 
        request: DownloadRequest,
        progress_callback: Optional[Callable[[DownloadProgress], None]] = None
    ) -> DownloadResult:
        """
        Descarga audio de YouTube según la solicitud.
        
        Args:
            request: Solicitud de descarga
            progress_callback: Callback para reportar progreso
            
        Returns:
            DownloadResult con el resultado de la descarga
        """
        # Validar solicitud
        is_valid, error_msg = request.validate()
        if not is_valid:
            return DownloadResult(
                success=False,
                video_title="",
                output_path="",
                error_message=error_msg
            )
        
        try:
            # Crear directorio de salida
            Path(request.output_dir).mkdir(parents=True, exist_ok=True)
            
            # Obtener información del video
            video_title = self._get_video_title(request.url)
            
            # Configurar opciones de yt-dlp
            ydl_opts = self._build_ydl_options(request, progress_callback)
            
            # Realizar descarga
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([request.url])
            
            # Construir ruta de salida
            output_path = os.path.join(
                request.output_dir, 
                f"{video_title}.{request.format}"
            )
            
            return DownloadResult(
                success=True,
                video_title=video_title,
                output_path=output_path
            )
            
        except Exception as e:
            return DownloadResult(
                success=False,
                video_title="",
                output_path="",
                error_message=str(e)
            )
    
    def _get_video_title(self, url: str) -> str:
        """Obtiene el título del video sin descargarlo."""
        info_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'Desconocido')
        except:
            return "Desconocido"
    
    def _get_expected_filename(self, url: str, output_dir: str, format: str) -> Optional[str]:
        """
        Obtiene el nombre exacto del archivo que yt-dlp crearía.
        Usa las mismas opciones que la descarga real.
        """
        try:
            info_opts = {
                'quiet': True,
                'no_warnings': True,
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            }
            
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    # Obtener el nombre base del archivo (sin extensión)
                    title = info.get('title', 'Desconocido')
                    return f"{title}.{format}"
        except:
            pass
        
        return None
    
    def _build_ydl_options(
        self, 
        request: DownloadRequest,
        progress_callback: Optional[Callable[[DownloadProgress], None]]
    ) -> dict:
        """Construye las opciones de configuración para yt-dlp."""
        
        def progress_hook(d):
            """Hook para reportar progreso de descarga."""
            if progress_callback is None:
                return
                
            if d['status'] == 'downloading':
                status = DownloadStatus.DOWNLOADING
                progress = 0.0
                downloaded_bytes = d.get('downloaded_bytes', 0) or 0
                total_bytes = d.get('total_bytes', 0) or 0
                speed = d.get('speed', 0) or 0
                eta = d.get('eta', 0) or 0
                
                if total_bytes > 0:
                    progress = downloaded_bytes / total_bytes
                
                # Formatear mensaje con más detalles
                speed_str = f"{speed / 1024 / 1024:.2f} MB/s" if speed > 0 else "0 MB/s"
                eta_str = f"{eta:.0f}s" if eta > 0 else "calculando..."
                downloaded_mb = downloaded_bytes / 1024 / 1024
                total_mb = total_bytes / 1024 / 1024 if total_bytes > 0 else 0
                
                # Truncar valores para que el mensaje no sea demasiado largo
                message = f"Descargando: {progress:.1%} | {downloaded_mb:.1f}MB/{total_mb:.1f}MB | {speed_str} | ETA: {eta_str}"
                
                progress_obj = DownloadProgress(
                    status=status,
                    progress=progress,
                    downloaded_bytes=downloaded_bytes,
                    total_bytes=total_bytes,
                    speed=speed,
                    eta=eta,
                    message=message
                )
                progress_callback(progress_obj)
                
            elif d['status'] == 'processing':
                # Progreso durante el procesamiento de audio
                progress = d.get('progress', 0) or 0
                message = f"Procesando audio: {progress:.1%}"
                
                progress_obj = DownloadProgress(
                    status=DownloadStatus.PROCESSING,
                    progress=progress,
                    message=message
                )
                progress_callback(progress_obj)
                
            elif d['status'] == 'finished':
                progress_obj = DownloadProgress(
                    status=DownloadStatus.PROCESSING,
                    progress=0.0,
                    message="Iniciando procesamiento de audio..."
                )
                progress_callback(progress_obj)
        
        def postprocessor_hook(d):
            """Hook para reportar progreso de postprocesamiento."""
            if progress_callback is None:
                return
                
            if d['status'] == 'processing':
                progress = d.get('progress', 0)
                message = f"Procesando audio: {progress:.1%}"
                
                progress_obj = DownloadProgress(
                    status=DownloadStatus.PROCESSING,
                    progress=progress,
                    message=message
                )
                progress_callback(progress_obj)
            elif d['status'] == 'finished':
                progress_obj = DownloadProgress(
                    status=DownloadStatus.PROCESSING,
                    progress=1.0,
                    message="Procesamiento completado"
                )
                progress_callback(progress_obj)
        
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': request.format,
                'preferredquality': request.quality,
            }],
            'outtmpl': os.path.join(request.output_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
            'ffmpeg_location': self.ffmpeg_path,
            # Configuraciones para evitar bloqueos de YouTube
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
            'nocheckcertificate': True,
        }
