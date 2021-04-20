import logging
import subprocess
import os
import time
import pathlib

try:
    from gtts import gTTS
except:
    pass

ONLINE_AUDIO_PATH = pathlib.Path(__file__).parent/"assets"/"online.mp3"
OFFLINE_AUDIO_PATH = pathlib.Path(__file__).parent/"assets"/"offline.mp3"


def generar_audio(audio_path, text, slow=False, lang="es"):
    try:
        audio_data = gTTS(text=text, lang=lang, slow=slow)
        audio_data.save(audio_path)
    except Exception as e:
        logging.error("Error al generar audio.")
        logging.error(e)
        raise e


def reproducir_audio(audio_path):
    try:
        subprocess.run(["vlc", audio_path, "--play-and-exit"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
    except Exception as e:
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
            en un futuro.
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
                   "que hayas configurado los datos de red correctamente "
                   "en el asistente.")

    online_msg = ("Estoy en línea.")
    generar_audio(OFFLINE_AUDIO_PATH, offline_msg)
    generar_audio(ONLINE_AUDIO_PATH, online_msg)
