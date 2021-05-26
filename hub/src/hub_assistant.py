# Copyright (C) 2017 Google Inc.
# Modifications copyright (C) 2021 Alan Fuentes, Yael Estrada, Noé Acosta
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Este código implementa un cliente gRPC para el API de Asistente de Google

    En éste módulo se importan las bibliotecas, módulos y se inicializan o
    establecen algunos parámetros para su ejecución e interacción con el API 
    de Google assistant.

"""

import concurrent.futures
import json
import logging
import os
import os.path
import sys

import click
import grpc
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials


from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)
from tenacity import retry, stop_after_attempt, retry_if_exception

from googlesamples.assistant.grpc import (
    assistant_helpers,
    audio_helpers,
)

from hub.src.voice_interface import hablar
from hub.src.hub_device_handler import create_hub_device_handler
from hub.src.voice_interface import ENTER_AUDIO_PATH, EXIT_AUDIO_PATH

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE

# Tiempo límite en segundos para la llamada al API Google Assistant
DEFAULT_GRPC_DEADLINE = 30

DEFAULT_LANGUAGE_CODE = "en-US"
CREDENTIALS_PATH = os.path.join(
    click.get_app_dir('google-oauthlib-tool'), 'credentials.json')


def create_conversation_stream():
    """ Crea un flujo de conversación con la fuente que se configura para
        la entrada y salida de audio.
        
        Returns:
            El objeto "conversation_stream" que servirá como la interfaz para
            establecer la conversación con el asistente de voz de Google.
    """

    audio_source = audio_sink = audio_helpers.SoundDeviceStream(
        sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,
        sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
        block_size=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
        flush_size=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
    )

    # Crea el flujo de conversación tomando la fuente de entrada y de salida
    # del audio, además de otros parámetros por defecto que vienen ya con el 
    # codigo del asistente de google.
    conversation_stream = audio_helpers.ConversationStream(
        source=audio_source,
        sink=audio_sink,
        iter_size=audio_helpers.DEFAULT_AUDIO_ITER_SIZE,
        sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
    )

    conversation_stream.volume_percentage = 100

    return conversation_stream


def create_grpc_channel():
    """ Crea el canal grpc que se comunicará con la API de Google Assistant
        para obtener las consultas que se realicen con el asistente de voz.

        Returns:
            El objeto grpc_channel que será el canal de comunicación para
            enviar peticiones a la API de Goole.
    """

    # Carga las credenciales OAuth 2.0 para acceder a la API de Google Assistant
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
            http_request = google.auth.transport.requests.Request()
            credentials.refresh(http_request)
    except Exception as e:
        logging.error('Error loading credentials: %s', e)
        logging.error('Run google-oauthlib-tool to initialize '
                      'new OAuth 2.0 credentials.')
        sys.exit(-1)

    # Una vez autorizado el acceso, se crea el canal grpc de comunicación a la API.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, ASSISTANT_API_ENDPOINT)
    logging.info('Connecting to %s', ASSISTANT_API_ENDPOINT)

    return grpc_channel

class HubAssistant(object):
    """ Asistente central que soporta conversaciones con el usuario y ejecuta
        las device actions.

        Attributes:
            language_code:
                Lenguaje por default del asistente
            device_model_id:
                Identificador del modelo del dispositivo.
            device_id: 
                Identificador de la instancia registrada del dispositivo.
            conversation_stream:
                Flujo de conversación del asistente.
            conversation_state:
                BLOB obtenido en la respuesta AssistResponse que da al Asistente
                un contexto del estado actual de la conversación multi-Assist()-RPC
                Este valor, junto con MicrophoneMode, soporta una conversación mas
                natural con el Asistente.
            is_new_conversation:
                Resetea para que la primer conversación
            grpc_channel:
                Crea el cliente gRPC para comunicarse con la API Google Assistant.
            assistant:
                Instancia del asistente de voz
            deadline:
                Tiempo de respuesta límite
            device_handler:
                Objeto para llamar a las device actions mediante callback
    """

    def __init__(self, device_model_id, device_id):
        """ Constructor donde se inicializan los parámetros de la clase.

            Args:
              device_model_id:
                Identificador del modelo del dispositivo.
              device_id: 
                Identificador de la instancia registrada del dispositivo.
        """
        self.language_code = DEFAULT_LANGUAGE_CODE
        self.device_model_id = device_model_id
        self.device_id = device_id
        self.conversation_stream = create_conversation_stream()
        self.conversation_state = None
        self.is_new_conversation = True
        grpc_channel = create_grpc_channel()
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            grpc_channel
        )
        self.deadline = DEFAULT_GRPC_DEADLINE
        self.device_handler = create_hub_device_handler(device_id)


    def __enter__(self):
        hablar(text=None, cache=ENTER_AUDIO_PATH)
        return self

    def __exit__(self, etype, e, traceback):
        if e:
            hablar(text=None, cache=EXIT_AUDIO_PATH)
            return False
        self.conversation_stream.close()

    def is_grpc_error_unavailable(e):
        """ Revisa la instancia del canal grp para comprobar si hay un
            error en el, si lo hay, levanta la excepcion y nos regresa
            True.

            Returns:
                Booleano que nos indica si hay o no un error con la conexión
                de gRPC.
        """
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            logging.error('grpc unavailable error: %s', e)
            return True
        return False


    @retry(reraise=True, stop=stop_after_attempt(5),
           retry=retry_if_exception(is_grpc_error_unavailable))
    def assist(self):
        """ Envía una solicitud de voz al asistente y reproduce la respuesta.

            Returns: 
                True si la conversación puede continuar.
        """
        continue_conversation = False
        device_actions_futures = []
        device_actions_requests = []

        self.conversation_stream.start_recording()
        logging.info('Recording audio request.')

        def iter_log_assist_requests():
            for c in self.gen_assist_requests():
                assistant_helpers.log_assist_request_without_audio(c)
                yield c
            logging.debug('Reached end of AssistRequest iteration.')

        """ Este generador reúne las respuestas del Asistente recibidas del
            canal gRPC de la API Google Assistant.
            Detecta el fin de la petición por comando de voz, envía la solicitud
            de transcripción del comando y nos regresa una respuesta de acuerdo
            a nuestra petición.
            Además si la petición invoca alguna device action, espera la ejecución
            de ésta y nos regresa una respuesta adecuada.
        """
        for resp in self.assistant.Assist(iter_log_assist_requests(),
                                          self.deadline):
            assistant_helpers.log_assist_response_without_audio(resp)
            if resp.event_type == END_OF_UTTERANCE:
                logging.info('End of audio request detected.')
                logging.info('Stopping recording.')
                self.conversation_stream.stop_recording()
            if resp.speech_results:
                logging.info('Transcript of user request: "%s".',
                             ' '.join(r.transcript
                                      for r in resp.speech_results))
            if len(resp.audio_out.audio_data) > 0:
                if not self.conversation_stream.playing:
                    self.conversation_stream.stop_recording()
                    self.conversation_stream.start_playback()
                    logging.info('Playing assistant response.')
                self.conversation_stream.write(resp.audio_out.audio_data)
            if resp.dialog_state_out.conversation_state:
                conversation_state = resp.dialog_state_out.conversation_state
                logging.debug('Updating conversation state.')
                self.conversation_state = conversation_state
            if resp.dialog_state_out.volume_percentage != 0:
                volume_percentage = resp.dialog_state_out.volume_percentage
                logging.info('Setting volume to %s%%', volume_percentage)
                self.conversation_stream.volume_percentage = volume_percentage
            if resp.dialog_state_out.microphone_mode == DIALOG_FOLLOW_ON:
                continue_conversation = True
                logging.info('Expecting follow-on query from user.')
            elif resp.dialog_state_out.microphone_mode == CLOSE_MICROPHONE:
                continue_conversation = False
            if resp.device_action.device_request_json:
                device_request = json.loads(
                    resp.device_action.device_request_json
                )
                device_actions_requests.append(device_request)

        for device_request in device_actions_requests:
            fs = self.device_handler(device_request)
            if fs:
                device_actions_futures.extend(fs)

        if len(device_actions_futures):
            logging.info('Waiting for device executions to complete.')
            concurrent.futures.wait(device_actions_futures)

        logging.info('Finished playing assistant response.')
        self.conversation_stream.stop_playback()
        return continue_conversation

    def gen_assist_requests(self):
        """ Genera el AssistRequest para comunicarse con la API
            
            Yields: 
                Mensajes del AssistRequest para enviar a la API.
        """

        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            dialog_state_in=embedded_assistant_pb2.DialogStateIn(
                language_code=self.language_code,
                conversation_state=self.conversation_state,
                is_new_conversation=self.is_new_conversation,
            ),
            device_config=embedded_assistant_pb2.DeviceConfig(
                device_id=self.device_id,
                device_model_id=self.device_model_id,
            )
        )

        # Continua la conversación actual con peticiones posteriores.
        self.is_new_conversation = False
        # El primer AssistRequest debe contener la configuración y no
        # los datos de audio.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        for data in self.conversation_stream:
            # Las peticiones subsecuentes necesitan los datos de audio, pero no la
            # configuración.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)
