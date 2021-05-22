import logging
import sys

import speech_recognition as sr
import click
from gpiozero import Button


# Recognizer for trigger word.
_recognizer = sr.Recognizer()

# Bandera de estado de conexión a internet.
# Será manejada por hilo de detección de conexión a internet.
status = {"online": False}


def wait_for_hot_word(hot_word):
    # Microphone listening.
    text = ""
    with sr.Microphone() as source:
        try:
            audio_data = _recognizer.listen(source)
            text = _recognizer.recognize_google(audio_data,
                                                language="es-MX")
        except sr.UnknownValueError:
            _recognizer.adjust_for_ambient_noise(source)
            logging.warning("Audio incorrecto. Intente de nuevo.")

        while hot_word.lower() not in text.lower():
            print("Palabra clave no detectada.")
            print("Detectando palabra clave...")
            try:
                audio_data = _recognizer.listen(source)
                text = _recognizer.recognize_google(audio_data,
                                                    language="es-MX")
            except:
                _recognizer.adjust_for_ambient_noise(source)
                print("Audio incorrecto. Intente de nuevo.")


def wait_for_button_pressed_and_released(button):
    button.wait_for_press()
    button.wait_for_release()


def wait_for_item(item, prop):
    while not item[prop]:
        pass


def get_trigger_function(trigger_message, waiter):
    def trigger_function():
        print(trigger_message)
        waiter()
    return trigger_function


# Configuración del detonador: botón, tecla, palabra/frase.
def define_trigger_waiter(trigger, word, button_pin):
    try:
        if trigger == "button":
            button = Button(button_pin)
            wait_for_trigger = get_trigger_function(
                "Presiona el botón para activar el asistente...",
                lambda: wait_for_button_pressed_and_released(button)
            )
        elif trigger == "key":
            wait_for_trigger = get_trigger_function(
                "Presiona una tecla para activar el asistente...",
                lambda: click.pause(None)
            )
        else:  # trigger == "word"
            assert word is not None and len(word) > 0
            wait_for_trigger = get_trigger_function(
                f"Di '{word}' para activar el asistente...",
                lambda: wait_for_hot_word(word)
            )

    except AssertionError:
        logging.error(("Debes proporcionar una palabra o frase "
                       "corta en --word dado que seleccionaste "
                       "el método de activación por palabra."))
        sys.exit(-1)
    except:
        logging.error(("Tu dispositivo no soporta botones físicos, "
                       "selecciona otro método de activación"))
        sys.exit(-1)

    return wait_for_trigger
