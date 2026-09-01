# DOW-MUSIC-MANUEL-DEV

Sistema con interfaz gráfica moderna para descargar audio de videos de YouTube en formato MP3.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Compilación](#compilación)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Solución de Problemas](#solución-de-problemas)

## ✨ Características

- **Interfaz gráfica moderna** con CustomTkinter
- **Búsqueda de videos de YouTube** - Encuentra videos directamente desde la aplicación
- **Previsualización de audio** - Escucha antes de descargar con reproductor profesional
- **Modo reproductor profesional** - Interfaz elegante con controles de reproducción
- **Archivos temporales** - Mantiene previsualizaciones para reutilización rápida
- **Validación en tiempo real** de URLs de YouTube
- **Detección de duplicados** - Evita descargar el mismo video múltiples veces
- **Limpieza automática** de URL después de descarga exitosa
- **Descarga la mejor calidad** de audio disponible
- **Convierte automáticamente** a MP3
- **Calidad de audio**: 192 kbps
- **Nombre de archivo** basado en el título del video
- **Barra de progreso** en tiempo real
- **Selector de directorio** de salida
- **Descarga en segundo plano** (no bloquea la interfaz)
- **Historial de descargas** automático
- **Logo personalizado** redondo
- **Icono personalizado** en barra de tareas
- **Interfaz adaptativa** - Se ajusta según el modo de uso

## 🔧 Requisitos

- Python 3.7 o superior
- Windows 10 o superior (para ejecutable .exe)

## 📦 Instalación

### 1. Descargar el Código

Opción A: Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Dowloader-music-mp3
```

Opción B: Descargar como ZIP
1. Descargar el archivo ZIP del repositorio
2. Extraer el contenido en una carpeta
3. Navegar a la carpeta extraída

### 2. Crear Entorno Virtual

```bash
python -m venv .venv
```

### 3. Activar Entorno Virtual

**Windows (PowerShell):**
```bash
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.venv\Scripts\activate.bat
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- `yt-dlp`: Librería para descargar videos de YouTube
- `customtkinter`: Interfaz gráfica moderna basada en Tkinter
- `imageio-ffmpeg`: FFmpeg empaquetado para procesamiento de audio
- `Pillow`: Manejo de imágenes (logo e icono)
- `pyinstaller`: Creación de ejecutables
- `pygame-ce`: Reproducción de audio para previsualización

## 🚀 Uso

### Ejecutar desde Código Fuente

```bash
python main.py
```

### Usar el Ejecutable

Si ya compilaste el proyecto, simplemente ejecuta:

```bash
dist\main.exe
```

### Usar el Instalador

Para instalar la aplicación en tu sistema:

```bash
dist\DOW-MUSIC-MANUEL-DEV_Setup.exe
```

### Interfaz de Usuario

#### Modo de Descarga (URL Directa)

1. **Campo URL**: Ingresa la URL del video de YouTube
   - Solo acepta URLs válidas de YouTube
   - Valida en tiempo real mientras escribes
   - Borra automáticamente URLs inválidas

2. **Directorio de Salida**: Selecciona dónde guardar el MP3
   - Por defecto: Carpeta "Downloads" del usuario
   - Usa el botón "Explorar" para cambiar ubicación

3. **Botón Descargar**: Inicia la descarga
   - Se deshabilita durante la descarga
   - Muestra progreso en tiempo real

4. **Barra de Progreso**: Muestra el avance de la descarga

5. **Área de Log**: Muestra mensajes de estado y errores

6. **Limpieza Automática**: El campo URL se limpia después de descarga exitosa

#### Modo de Búsqueda

1. **Campo de Búsqueda**: Busca videos de YouTube por nombre
   - Muestra hasta 10 resultados
   - Incluye título, duración y canal

2. **Resultados de Búsqueda**: Lista de videos encontrados
   - Radio buttons para seleccionar video
   - Botón de reproducción (▶) para previsualizar
   - Información detallada de cada resultado

3. **Previsualización de Audio**:
   - Descarga temporal del audio en directorio temporal
   - Reproductor profesional con controles
   - Logo personalizado del modo reproductor
   - Barra de progreso visual
   - Botones: Anterior, Pausar, Reproducir, Detener, Siguiente
   - Botón "Volver a Búsqueda" para regresar

4. **Reutilización de Archivos Temporales**:
   - Los archivos de previsualización se mantienen
   - Al volver a reproducir la misma canción, no se descarga de nuevo
   - Solo se descarga al cambiar de canción

#### Comportamiento de la Interfaz

- **Logo siempre visible** excepto en modo reproductor (que tiene su propio logo)
- **Modo búsqueda**: Solo muestra resultados y log (oculta directorio y controles de descarga)
- **Modo reproductor**: Muestra interfaz profesional dedicada (oculta todos los demás elementos)
- **Vista normal**: Muestra todos los elementos para descarga por URL

## 🔨 Compilación

### Compilación Automática (Recomendado)

**Opción A: Script PowerShell (Recomendado para Windows)**

Usa el script `build.ps1`:

```powershell
.\build.ps1
```

Este script:
- Borra el ejecutable anterior si existe
- Borra el directorio build anterior si existe
- Compila con PyInstaller
- Genera instalador con NSIS (si está disponible)
- Muestra mensaje de éxito o error

**Opción B: Script Batch (Alternativa)**

Usa el script `build.bat`:

```bash
.\build.bat
```

**Archivos generados:**
- **Ejecutable**: `dist\main.exe` - Ejecutable standalone
- **Instalador**: `dist\DOW-MUSIC-MANUEL-DEV_Setup.exe` - Instalador profesional con desinstalador

### Requisitos para el Instalador

Para generar el instalador, necesitas tener NSIS instalado:
1. Descarga NSIS desde: https://nsis.sourceforge.io/Download
2. Instala NSIS en tu sistema
3. Asegúrate de que `makensis` esté en el PATH del sistema

Si NSIS no está disponible, el script solo generará el ejecutable standalone.

### Compilación Manual (Solo Ejecutable)

Si prefieres compilar solo el ejecutable manualmente:

```bash
.venv\Scripts\pyinstaller.exe --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --add-data "logo.png;." --add-data "src;src" main.py
```

**Parámetros:**
- `--onefile`: Crea un solo archivo ejecutable
- `--windowed`: Ejecuta sin consola (modo gráfico)
- `--icon=icon.ico`: Establece el icono del ejecutable
- `--add-data`: Incluye archivos necesarios (icono, logo, código fuente)

### Generación Manual del Instalador

Si ya tienes el ejecutable compilado y quieres generar solo el instalador:

```bash
makensis installer.nsi
```

El instalador se creará en: `dist\DOW-MUSIC-MANUEL-DEV_Setup.exe`

### Ubicación de los Archivos

- **Ejecutable standalone**: `dist\main.exe`
- **Instalador**: `dist\DOW-MUSIC-MANUEL-DEV_Setup.exe`

### Diferencias entre Ejecutable e Instalador

**Ejecutable Standalone (`main.exe`):**
- Archivo único, portable
- No requiere instalación
- Solo copiar y ejecutar
- El historial de descargas se crea en el mismo directorio del ejecutable

**Instalador (`DOW-MUSIC-MANUEL-DEV_Setup.exe`):**
- **Instalación profesional con asistente** - Interfaz moderna con páginas de bienvenida, licencia y componentes
- **Verificación de requisitos** - Comprueba Windows 10+
- **Detección de instalación previa** - Ofrece desinstalar versiones anteriores automáticamente
- **Accesos directos** - Crea accesos directos en escritorio y menú de inicio
- **Instalación en Program Files** - Ubicación estándar de Windows
- **Desinstalador completo** - Incluye desinstalador con opción de conservar datos de usuario
- **Registro en Panel de Control** - Aparece en Programas y Características
- **Opción de ejecutar al finalizar** - Permite ejecutar la aplicación inmediatamente después de la instalación
- **Acceso directo al sitio web** - Enlace directo a la página del proyecto
- **El historial de descargas se crea en `%APPDATA%\DOW-MUSIC-MANUEL-DEV`**
- **Icono personalizado** - Utiliza el icono de la aplicación en todo el instalador

## 🏗️ Arquitectura del Proyecto

El proyecto sigue una arquitectura modular con separación de responsabilidades:

```
Dowloader-music-mp3/
├── src/
│   ├── config/           # Configuración y constantes
│   │   └── config.py    # AppConfig - maneja configuración
│   ├── models/          # Modelos de datos
│   │   ├── download_models.py    # DownloadRequest, DownloadProgress, DownloadResult
│   │   ├── download_history.py   # DownloadHistory - historial de descargas
│   │   └── search_models.py      # SearchResult - modelo para resultados de búsqueda
│   ├── services/        # Lógica de negocio
│   │   ├── download_service.py    # DownloadService - maneja descargas
│   │   ├── search_service.py      # SearchService - maneja búsqueda de videos
│   │   └── audio_player_service.py # AudioPlayerService - maneja reproducción de audio
│   ├── ui/              # Interfaz gráfica
│   │   └── main_window.py         # MainWindow - interfaz principal
│   └── utils/           # Utilidades
│       └── image_utils.py         # ImageUtils - procesamiento de imágenes
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
├── build.bat           # Script de compilación
├── icon.ico            # Icono de la aplicación
├── logo.png            # Logo de la interfaz
└── download_history.json # Historial de descargas (se crea automáticamente)
```

### Módulos Principales

**Config (`src/config/`)**
- Maneja configuración de la aplicación
- Constantes y rutas de recursos

**Models (`src/models/`)**
- Estructuras de datos para descargas
- Validación de URLs
- Historial de descargas
- Modelos para resultados de búsqueda de YouTube

**Services (`src/services/`)**
- **DownloadService**: Lógica de negocio para descargas
- **SearchService**: Búsqueda de videos de YouTube
- **AudioPlayerService**: Reproducción de audio con pygame-ce
- Integración con yt-dlp
- Gestión de FFmpeg

**UI (`src/ui/`)**
- Interfaz gráfica con CustomTkinter
- Manejo de eventos del usuario
- Actualización de progreso
- Modo reproductor profesional
- Gestión de búsqueda y previsualización

**Utils (`src/utils/`)**
- Procesamiento de imágenes
- Utilidades generales

## 🔍 Solución de Problemas

### Error: "No se encuentra el entorno virtual"

**Solución:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "La URL no es válida"

**Solución:**
- Asegúrate de usar una URL de YouTube válida
- Formatos aceptados:
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://www.youtube.com/embed/VIDEO_ID`

### Error: "El video ya fue descargado"

**Solución:**
- El sistema evita duplicados automáticamente
- Si quieres descargar nuevamente, borra el archivo MP3 existente
- O borra el archivo `download_history.json`

### Error: "HTTP Error 403: Forbidden"

**Solución:**
- Este error puede ocurrir si YouTube bloquea la descarga
- Intenta actualizar yt-dlp: `pip install --upgrade yt-dlp`
- Verifica que la URL sea correcta y el video sea público

### El ejecutable no muestra el icono

**Solución:**
- Asegúrate de compilar con el parámetro `--icon=icon.ico`
- El icono solo aparece correctamente en el ejecutable, no al ejecutar el .py

### La interfaz no responde al redimensionar

**Solución:**
- La interfaz usa sistema grid responsive
- Asegúrate de tener la versión más reciente del código
- El tamaño mínimo de ventana es 400x500

## 📝 Notas Adicionales

- El historial de descargas se guarda en `download_history.json`
- El archivo se crea automáticamente en el directorio del ejecutable
- El historial incluye: URL, título, ruta, fecha y tamaño del archivo
- Los archivos que ya no existen se eliminan automáticamente del historial

## 🤝 Contribuciones

Este proyecto está diseñado para ser fácilmente extensible:

- **Agregar nuevas funcionalidades**: Crea nuevos servicios en `src/services/`
- **Modificar la interfaz**: Edita `src/ui/main_window.py`
- **Cambiar configuración**: Modifica `src/config/config.py`
- **Agregar nuevos modelos**: Crea en `src/models/`

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
