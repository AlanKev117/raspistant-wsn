import logging
import pathlib
import subprocess

from gtts import gTTS

ONLINE_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"online.mp3"
OFFLINE_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"offline.mp3"
ERROR_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"error.mp3"
TELLME_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"tellme.mp3"
SERVICE_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"service.mp3"
SHUTDOWN_AUDIO_PATH = pathlib.Path(
    __file__).parent.parent/"assets"/"shutdown.mp3"


def generar_audio(audio_path, text, slow=False, lang="es"):
    """Sintetiza un archivo de audio con el contenido, idioma y velocidad
    requeridas utilizando el servicio de síntesis de voz de Google.

    Args:
        audio_path: La ruta destino del archivo de audio sintetizado
        text: Contenido de texto a sintetizar
        slow: Indica si el audio debería guardar una reproducción lenta
            del contenido
        lang: Código del idioma en el que se sintetizará el audio requerido

    Raises:
        gTTSError: Si hubo un error en la petición al servidor de síntesis
        FileNotFoundError: Si la ruta del archivo destino no puede ser accedida

    """
    try:
        audio_data = gTTS(text=text, lang=lang, slow=slow)
        audio_data.save(audio_path)
    except Exception as e:
        logging.error("Error al generar audio.")
        logging.error(e)
        raise e


def reproducir_audio(audio_path):
    """Reproduce un audio encontrado en la ruta proporcionada
    invocando el plugin del reproductor vlc para Python.

    Args:
        audio_path: La ruta al archivo de audio a reproducir

    Raises:
        FileNotFoundError: Si el archivo de audio o el comando vlc 
            no se encuentran
    """
    try:
        audio_file = pathlib.Path(audio_path)
        if audio_file.exists():
            subprocess.run(["mpg123", audio_file],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           check=True)
        else:
            raise FileNotFoundError("Archivo de audio no encontrado")
    except FileNotFoundError as e:
        logging.error("Error al reproducir audio.")
        logging.error(e)
        raise e


def hablar(text, slow=False, lang="es", cache=None):
    """Reproduce una cadena de texto proporcionada en forma de audio.

    Args:
        text: la cadena a ser sintetizada y pronunciada.
        slow: indica si se debe prounciar lento o no.
        lang: código del idioma en el que la cadena está escrita.
        cache: indica la ruta para guardar el audio para ser usado de nuevo
            sin conexión en un futuro.

    Raises:
        FileNotFoundError: Si el archivo de audio a reproducir o el comando vlc 
            no se encuentran o si la ruta del archivo destino no puede ser 
            accedida al sintetizar audio
        gTTSError: Si hubo un error en la petición al servidor de síntesis al
            sintetizar audio
    """

    audio_path = cache or "/tmp/assistant_audio.mp3"
    audio_path = pathlib.Path(audio_path)
    try:

        if not audio_path.exists():
            generar_audio(audio_path, text, slow=slow, lang=lang)

        reproducir_audio(audio_path)

        if not cache:
            audio_path.unlink()

    except Exception as e:

        logging.error("Error al pronunciar cadena.")
        logging.error(e)
        raise e


if __name__ == "__main__":
    offline_msg = ("No tengo conexión a internet. "
                   "Revisa que todo esté en orden con tu módem y "
                   "que tu asistente tenga los datos de red adecuados.")
    online_msg = "Estoy en línea."
    error_msg = "Ocurrió un error inesperado en el asistente."
    tellme_msg = "Dime."
    service_msg = "No me pude conectar al servicio de asistencia de voz."
    shutdown_msg = "Apagando tu dispositivo. Hasta pronto."

    generar_audio(OFFLINE_AUDIO_PATH, offline_msg)
    generar_audio(ONLINE_AUDIO_PATH, online_msg)
    generar_audio(ERROR_AUDIO_PATH, error_msg)
    generar_audio(TELLME_AUDIO_PATH, tellme_msg)
    generar_audio(SERVICE_AUDIO_PATH, service_msg)
    generar_audio(SHUTDOWN_AUDIO_PATH, shutdown_msg)
