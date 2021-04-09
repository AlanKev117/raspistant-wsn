from playsound import playsound
import os
import logging
from gtts import gTTS

def reproducirVoz(cadena):
    lan="es"
    try:
    	myobj=gTTS(text=cadena,lang=lan,slow=False)
    	myobj.save('/tmp/voice_command.mp3')
    	playsound('/tmp/voice_command.mp3')
    	os.remove('/tmp/voice_command.mp3')
    	return True
    except:
    	print("ERROR AL CREAR EL ARCHIVO DE RESPUESTA DE VOZ")
    	return False;


reproducirVoz("Huevos kevin!")