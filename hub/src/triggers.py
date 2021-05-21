import logging

import speech_recognition as sr

# Recognizer for trigger word.
_recognizer = sr.Recognizer()

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

def get_trigger_function(trigger_message, waiter):
    def trigger_function():
        print(trigger_message)
        waiter()
    return trigger_function
