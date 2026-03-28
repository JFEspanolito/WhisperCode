# region Configuración del entorno
# Presiona Ctrl + Shift + P
# Escribe: Python: Select Interpreter
# Elige la ruta que apunta a:
# F:\Software\IDE\Python\x64\Python3.10\python.exe
# Ejecutar
# python WhisperOpenAI.py

import subprocess
import os
import sys
import shutil

try:
    import whisper
except ModuleNotFoundError:
    print("Falta el paquete 'openai-whisper' en el interprete activo.")
    print("Instalalo con: pip install openai-whisper")
    sys.exit(1)

# region Configuración de rutas
# Ruta del directorio a analizar
rutaInputs = r"F:\Software\IA\Whisper OpenAI\WhisperCode\inputs"
# Nota: la variable conserva el nombre original (rutaOuputs) para mantener compatibilidad
rutaOuputs = r"F:\Software\IA\Whisper OpenAI\WhisperCode\outputs"
# Config: conservar MP3 generados (True = los mantiene en outputs/mp3s/, False = los elimina tras transcribir)
KEEP_MP3 = True
# endregion

# region Verificar directorios & Cambio de formato en archivos si es necesario
# Extensiones permitidas (audio y video)
ext_permitidas = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".mp4", ".mkv", ".mov", ".avi"]

# Recolectar todos los archivos válidos en la carpeta de inputs
archivos_validos = [f for f in os.listdir(rutaInputs)
                    if os.path.splitext(f)[1].lower() in ext_permitidas]

if not archivos_validos:
    raise FileNotFoundError("No se encontró ningún archivo de audio o video válido en el directorio.")

# Asegurar que la carpeta de salida exista
os.makedirs(rutaOuputs, exist_ok=True)
# Carpeta para mp3 generados (si KEEP_MP3 True se conservarán aquí)
mp3_dir = os.path.join(rutaOuputs, "mp3s")
os.makedirs(mp3_dir, exist_ok=True)

# Verificar disponibilidad de ffmpeg
ffmpeg_cmd = shutil.which("ffmpeg")
if ffmpeg_cmd is None:
    # 1) Permitir al usuario especificar FFMPEG_PATH como variable de entorno
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path and os.path.isfile(env_path):
        ffmpeg_cmd = env_path
    else:
        # 2) Buscar ffmpeg.exe dentro del proyecto (carpeta del script)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        found = None
        for root, dirs, files in os.walk(base_dir):
            if "ffmpeg.exe" in files:
                found = os.path.join(root, "ffmpeg.exe")
                break

        # 3) Comprobar ubicaciones comunes en Windows
        common_paths = [r"F:\Software\IA\Whisper OpenAI\ffmpeg\bin\ffmpeg.exe", r"F:\Software\IA\Whisper OpenAI\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"]
        for p in common_paths:
            if found:
                break
            if os.path.isfile(p):
                found = p
                break

        if found:
            ffmpeg_cmd = found
            print(f"Usando ffmpeg encontrado en: {ffmpeg_cmd}")
        else:
            print("Error: 'ffmpeg' no está disponible en PATH ni se encontró en el proyecto.")
            print("Opciones: (1) Instala ffmpeg y añade su carpeta 'bin' al PATH, (2) define la variable de entorno FFMPEG_PATH con la ruta a ffmpeg.exe, o (3) coloca ffmpeg.exe en la carpeta del proyecto.")
            print("Descargas: https://ffmpeg.org/download.html")
            sys.exit(1)

# Cargar modelo una sola vez
print("Cargando modelo Whisper...")
try:
    model = whisper.load_model("base")
except Exception as e:
    print("Error cargando el modelo Whisper:", e)
    sys.exit(1)

# Extensiones que se consideran video (para extraer audio con -map a)
video_exts = {".mp4", ".mkv", ".mov", ".avi"}

# Procesar cada archivo
for archivo in archivos_validos:
    ruta_original = os.path.join(rutaInputs, archivo)
    nombre_base, extension = os.path.splitext(os.path.basename(ruta_original))
    extension = extension.lower()

    # Determinar ruta del mp3 que se usará para transcribir
    if extension == ".mp3":
        ruta_mp3 = ruta_original
        creado_temporal = False
    else:
        # Guardar mp3 generado en la carpeta de salida para que sea visible
        ruta_mp3 = os.path.join(mp3_dir, nombre_base + ".mp3")
        creado_temporal = not KEEP_MP3

        print(f"Convirtiendo '{archivo}' ({extension}) a MP3...")
        if extension in video_exts:
            cmd = [ffmpeg_cmd, "-y", "-i", ruta_original, "-q:a", "0", "-map", "a", ruta_mp3]
        else:
            cmd = [ffmpeg_cmd, "-y", "-i", ruta_original, ruta_mp3]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error convirtiendo {archivo}:", e)
            # Intentar continuar con el siguiente archivo
            continue
# Convertir archivo de audio a mp3
# ffmpeg -i audio.ogg audio.mp3

# Convertir archivo de video a mp3
# -q:a 0: máxima calidad de audio en VBR
# -map a: extrae solo la pista de audio
# ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3
# endregion

    # Transcribir
    print(f"Transcribiendo '{archivo}'...")
    try:
        result = model.transcribe(ruta_mp3, language="es")
    except Exception as e:
        print(f"Error transcribiendo {archivo}:", e)
        # Cleanup temporal si existe
        if creado_temporal and os.path.exists(ruta_mp3):
            try:
                os.remove(ruta_mp3)
            except Exception:
                pass
        continue

    texto = result.get("text", "")
    print("Texto transcrito:\n", texto)

    # Guardar a archivo
    nombre_salida = nombre_base + "_transcripcion.txt"
    ruta_salida = os.path.join(rutaOuputs, nombre_salida)
    try:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"Transcripción guardada en: {ruta_salida}")
    except Exception as e:
        print(f"Error guardando la transcripción de {archivo}:", e)

    # Eliminar mp3 temporal si fue creado y CONFIG indica no conservar
    if (not KEEP_MP3) and creado_temporal and os.path.exists(ruta_mp3):
        try:
            os.remove(ruta_mp3)
        except Exception:
            pass

print("Procesamiento completado.")