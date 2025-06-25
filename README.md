# Prueba de Whisper de OpenAI

Este script permite probar el modelo `whisper` de OpenAI para transcripción automática de audio o video a texto en español.

## Funcionalidad

1. Escanea un directorio en busca del primer archivo de audio o video válido.
2. Si no está en formato `.mp3`, lo convierte automáticamente usando `ffmpeg`.
3. Usa el modelo `whisper` de OpenAI (versión `base`) para transcribir el audio.
4. Muestra el texto transcrito por consola.
5. Guarda el resultado en un archivo `.txt` con el mismo nombre que el archivo original.

## Requisitos

- Python 3.10
- [whisper](https://github.com/openai/whisper)
- `ffmpeg` instalado y accesible en la línea de comandos.

## Uso

1. Asegúrate de tener instalado el intérprete correcto:
   - `F:\Software\IDE\Python\x64\Python3.10\python.exe`
2. Coloca un archivo de audio o video compatible en el directorio:
   - `F:\Software\IA\Whisper OpenAI`
3. Ejecuta el script `WhisperOpenAI.py`.
4. El resultado se mostrará en consola y se guardará como `.txt`.

## Formatos compatibles

- Audio: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`
- Video: `.mp4`, `.mkv`, `.mov`, `.avi`