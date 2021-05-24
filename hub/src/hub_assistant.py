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

"""Sample that implements a gRPC client for the Google Assistant API."""

import concurrent.futures
from hub.src.voice_interface import hablar
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

from hub.src.hub_device_handler import create_hub_device_handler
from hub.src.voice_interface import ENTER_AUDIO_PATH, EXIT_AUDIO_PATH

ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE

# gRPC deadline in seconds for Google Assistant API call
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5

DEFAULT_LANGUAGE_CODE = "en-US"
CREDENTIALS_PATH = os.path.join(
    click.get_app_dir('google-oauthlib-tool'), 'credentials.json')


def create_conversation_stream():
    # Configure audio source and sink.
    audio_source = audio_sink = audio_helpers.SoundDeviceStream(
        sample_rate=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,
        sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
        block_size=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
        flush_size=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
    )

    # Create conversation stream with the given audio source and sink
    # for recording query and playing back assistant answer
    conversation_stream = audio_helpers.ConversationStream(
        source=audio_source,
        sink=audio_sink,
        iter_size=audio_helpers.DEFAULT_AUDIO_ITER_SIZE,
        sample_width=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
    )

    conversation_stream.volume_percentage = 100

    return conversation_stream


def create_grpc_channel():
    # Load OAuth 2.0 credentials.
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

    # Create an authorized gRPC channel.
    grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, ASSISTANT_API_ENDPOINT)
    logging.info('Connecting to %s', ASSISTANT_API_ENDPOINT)

    return grpc_channel

class HubAssistant(object):
    """Hub Assitant that supports conversations and device actions.

    Args:
      device_model_id: identifier of the device model.
      device_id: identifier of the registered device instance.
    """

    def __init__(self, device_model_id, device_id):

        self.language_code = DEFAULT_LANGUAGE_CODE

        self.device_model_id = device_model_id
        self.device_id = device_id

        self.conversation_stream = create_conversation_stream()

        # Opaque blob provided in AssistResponse that,
        # when provided in a follow-up AssistRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Assist()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        self.conversation_state = None

        # Force reset of first conversation.
        self.is_new_conversation = True

        # Create Google Assistant API gRPC client.
        grpc_channel = create_grpc_channel()
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            grpc_channel
        )

        self.deadline = DEFAULT_GRPC_DEADLINE

        # Callback for device actions.
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
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            logging.error('grpc unavailable error: %s', e)
            return True
        return False

    @retry(reraise=True, stop=stop_after_attempt(5),
           retry=retry_if_exception(is_grpc_error_unavailable))
    def assist(self):
        """Send a voice request to the Assistant and playback the response.

        Returns: True if conversation should continue.
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

        # This generator yields AssistResponse proto messages
        # received from the gRPC Google Assistant API.
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
        """Yields: AssistRequest messages to send to the API."""

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

        # Continue current conversation with later requests.
        self.is_new_conversation = False
        # The first AssistRequest must contain the AssistConfig
        # and no audio data.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)
