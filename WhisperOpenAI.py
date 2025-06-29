#region Configuración del entorno
# Presiona Ctrl + Shift + P
# Escribe: Python: Select Interpreter
# Elige la ruta que apunta a:
# F:\Software\IDE\Python\x64\Python3.10\python.exe
import whisper
import subprocess
import os
#endregion

#region Configuración de rutas
# Ruta del directorio a analizar
rutaInputs = r"F:\Software\IA\Whisper OpenAI\WhisperCode\inputs"
rutaOuputs = r"F:\Software\IA\Whisper OpenAI\WhisperCode\outputs"
#endregion

#region Verificar directorios & Cambio de formato en archivos si es necesario
# Extensiones permitidas (audio y video)
ext_permitidas = [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".mp4", ".mkv", ".mov", ".avi"]

# Buscar primer archivo válido
ruta_original = None
for archivo in os.listdir(rutaInputs):
    if os.path.splitext(archivo)[1].lower() in ext_permitidas:
        ruta_original = os.path.join(rutaInputs, archivo)
        break

if not ruta_original:
    raise FileNotFoundError("No se encontró ningún archivo de audio o video válido en el directorio.")

# Procesar como antes
nombre_base, extension = os.path.splitext(ruta_original)
extension = extension.lower()
ruta_mp3 = nombre_base + ".mp3"

# Si no es mp3, convertirlo
if extension != ".mp3":
    print(f"Convirtiendo {extension} a .mp3...")

    if extension in [".mp4", ".mkv", ".mov", ".avi"]:
        cmd = ["ffmpeg", "-i", ruta_original, "-q:a", "0", "-map", "a", ruta_mp3]
    else:
        cmd = ["ffmpeg", "-i", ruta_original, ruta_mp3]

    subprocess.run(cmd, check=True)
# Convertir archivo de audio a mp3
# ffmpeg -i audio.ogg audio.mp3

# Convertir archivo de video a mp3 
# -q:a 0: máxima calidad de audio en VBR
# -map a: extrae solo la pista de audio
# ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3
#endregion

#region Transcripción con Whisper
#region Modelo & Transcripción
# Cargar modelo
model = whisper.load_model("base")

# Transcribir
result = model.transcribe(ruta_mp3, language="es")
print("Texto transcrito:\n", result["text"])
#endregion

# Guardar a archivo
nombre_salida = os.path.basename(nombre_base) + "_transcripcion.txt"
ruta_salida = os.path.join(rutaOuputs, nombre_salida)
with open(ruta_salida, "w", encoding="utf-8") as f:
    f.write(result["text"])
#endregion