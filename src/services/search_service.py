"""
Servicio de búsqueda de videos en YouTube.
Maneja la lógica de búsqueda usando yt-dlp.
"""
import yt_dlp
from typing import List, Optional
from src.models.search_models import SearchResult, SearchRequest


class SearchService:
    """Servicio que maneja la búsqueda de videos en YouTube."""
    
    def search_videos(self, request: SearchRequest) -> tuple[bool, Optional[List[SearchResult]], Optional[str]]:
        """
        Busca videos en YouTube según la consulta.
        
        Args:
            request: Solicitud de búsqueda
            
        Returns:
            (exito, resultados, mensaje_error)
        """
        try:
            # Validar solicitud
            is_valid, error_msg = request.validate()
            if not is_valid:
                return False, None, error_msg
            
            # Configurar opciones de yt-dlp para búsqueda con resiliencia de red
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Solo obtener metadatos, no descargar
                'max_downloads': request.max_results,
                'socket_timeout': 15,
                'retries': 10,
                'retry_sleep': 2,
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            # Realizar búsqueda
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Usar ytsearch para buscar
                search_query = f"ytsearch{request.max_results}:{request.query}"
                results = ydl.extract_info(search_query, download=False)
                
                if not results or 'entries' not in results:
                    return False, None, "No se encontraron resultados"
                
                # Convertir resultados a modelo
                search_results = []
                for entry in results['entries']:
                    if entry and isinstance(entry, dict):
                        video_id = entry.get('id', '')
                        if not video_id:
                            continue
                        
                        url = entry.get('webpage_url') or entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                        if not url.startswith("http"):
                            url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        result = SearchResult(
                            video_id=video_id,
                            title=entry.get('title', 'Desconocido'),
                            url=url,
                            thumbnail_url=entry.get('thumbnail'),
                            duration=self._format_duration(entry.get('duration')),
                            view_count=entry.get('view_count'),
                            uploader=entry.get('uploader', 'Desconocido')
                        )
                        search_results.append(result)
                
                if not search_results:
                    return False, None, "No se encontraron resultados válidos"
                
                return True, search_results, None
                
        except yt_dlp.utils.DownloadError as e:
            err_str = str(e)
            if self._is_network_error(err_str):
                return False, None, "Sin conexión a Internet. Por favor verifica tu red."
            return False, None, f"Error en búsqueda: {err_str}"
        except Exception as e:
            err_str = str(e)
            if self._is_network_error(err_str):
                return False, None, "Sin conexión a Internet. Por favor verifica tu red."
            return False, None, f"Error en búsqueda: {str(e)}"
    
    def _is_network_error(self, err_msg: str) -> bool:
        """Determina si un mensaje de error corresponde a falta de red/Internet."""
        err_lower = err_msg.lower()
        terms = [
            "getaddrinfo", "11001", "gaierror", "name or service not known",
            "nodename nor servname", "unreachable", "timed out", "timeout",
            "connection", "connect", "network", "socket", "offline",
            "transporterror", "http error", "unable to download", "no route to host",
            "requested format is not available", "only images are available"
        ]
        return any(t in err_lower for t in terms)
    
    def _format_duration(self, duration: Optional[int]) -> Optional[str]:
        """Formatea la duración en segundos a formato HH:MM:SS."""
        if duration is None:
            return None
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
