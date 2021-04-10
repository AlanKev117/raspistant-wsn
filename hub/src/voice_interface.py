import logging
import os
from playsound import playsound
from gtts import gTTS


def reproducir_voz(text, slow=False, lang="es"):
    """Reproduce una cadena de texto proporcionada en forma de audio.

    Args:
        text: la cadena a ser sintetizada y pronunciada.
        slow: indica si se debe prounciar lento o no.
        lang: código del idioma en el que la cadena está escrita.

    """

    audio_path = "/tmp/assistant_audio.mp3"

    try:

        audio_data = gTTS(text=text, lang=lang, slow=slow)
        audio_data.save(audio_path)
        playsound(audio_path)
        os.remove(audio_path)

    except Exception as e:
    
        try:
            
            os.remove(audio_path)
        
        except FileNotFoundError:
            
            logging.warning("No se generó audio.")
            
        logging.error("Error al pronunciar cadena.")
        logging.error(e)
        
        raise e
        