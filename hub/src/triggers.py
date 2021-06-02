""" Triggers

    Éste código implementa los lanzadores que activan el asistente de voz
"""

import logging
import sys

import click
from gpiozero import Button

from hub.src.voice_interface import TRIGGER_AUDIO_PATH, reproducir_audio


def wait_for_button_pressed_and_released(button):
    """Espera por un ciclo completo de activación de un botón físico.
    
    Args:
        button: el objeto que abstrae el botón físico.
    """
    button.wait_for_press()
    button.wait_for_release()


def get_trigger_function(trigger_message, waiter):
    """Función auxiliar que genera un activador
    
    Args:
        trigger_message: mensaje o instruccion para continuar.
        waiter: función que pausa el flujo de instrucciones.
    """
    def trigger_function():
      
        # Se imprime la instrucción para detonar el activador
        print(trigger_message)
        waiter()
        
        # Se reproduce un audio confirmando que el activador fue
        # detonado.
        reproducir_audio(TRIGGER_AUDIO_PATH)
    return trigger_function


def define_trigger_waiter(trigger, button_pin):
    """Define la función activadora el asistente de voz.
    
    Args:
        trigger: define si la función invloucra presionar una tecla
            ("key") o un botón ("button").
        button_pin: en caso de ser "button" el argumento anterior,
            indica el pin GPIO que donde se conectará el botón a usar.
    """
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
