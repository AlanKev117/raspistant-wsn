from playsound import playsound
import os
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
    	return False;