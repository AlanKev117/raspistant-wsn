import logging
import sys

import click
from gpiozero import Button

from hub.src.voice_interface import TRIGGER_AUDIO_PATH, reproducir_audio


def wait_for_button_pressed_and_released(button):
    button.wait_for_press()
    button.wait_for_release()


def get_trigger_function(trigger_message, waiter):
    def trigger_function():
        print(trigger_message)
        waiter()
        reproducir_audio(TRIGGER_AUDIO_PATH)
    return trigger_function


# Configuración del detonador: botón, tecla, palabra/frase.
def define_trigger_waiter(trigger, button_pin):
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
    except:
        logging.error(("Tu dispositivo no soporta botones físicos, "
                       "selecciona otro método de activación"))
        sys.exit(-1)

    return wait_for_trigger
