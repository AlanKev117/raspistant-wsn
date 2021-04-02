import logging

import click

try:
    from .hub_assistant import HubAssistant
except (SystemError, ImportError):
    from hub_assistant import HubAssistant

@click.command()
@click.option('--device-model-id',
              metavar='<device model id>',
              help=(('Unique device model identifier, '
                      'if not specifed, it is read from --device-config')))
@click.option('--device-id',
              metavar='<device id>',
              help=(('Unique registered device instance identifier, '
                      'if not specified, it is read from --device-config, '
                      'if no device_config found: a new device is registered '
                      'using a unique id and a new device config is saved')))
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Verbose logging.')
def main(device_model_id, device_id, verbose):

    # Setup global logger
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

    with HubAssistant(device_model_id, device_id) as hub_assistant:

        # Record voice requests using the microphone
        # and play back assistant response using the speaker.
        wait_for_user_trigger = True
        while True:
            if wait_for_user_trigger:
                click.pause(info='Press Enter to send a new request...')
            continue_conversation = hub_assistant.assist()
            # wait for user trigger if there is no follow-up turn in
            # the conversation.
            wait_for_user_trigger = not continue_conversation


if __name__ == '__main__':
    main()
