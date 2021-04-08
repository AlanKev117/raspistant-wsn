import logging

import click

try:
    from .hub_assistant import HubAssistant, DEVICE_CONFIG_PATH
except (SystemError, ImportError):
    from hub_assistant import HubAssistant, DEVICE_CONFIG_PATH


@click.command()
@click.option('--device-model-id', '--model',
              metavar='<device model id>',
              help=(('Identificador del modelo registrado del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. '
                     'Si no se encuentra el archivo, se darán instrucciones '
                     'avanzadas.')))
@click.option('--device-id', '--device',
              metavar='<device id>',
              help=(('Identificador de instancia registrada del dispositivo. '
                     'Si no se especifica, se lee del archivo '
                     f'{DEVICE_CONFIG_PATH}. '
                     'Si no se encuentra el archivo, se darán instrucciones '
                     'avanzadas.')))
@click.option('--trigger', '-t',
              type=click.Choice(['keystroke', 'hotword']),
              default='keystroke',
              help=(('Seleccione "keystroke" para activar el asistente con '
                     'cualquier tecla del teclado o seleccione "hotword" para '
                     'activarlo al pronunciar "Ok Google".')))
@click.option('--verbose', '-v',
              is_flag=True,
              default=False,
              help='Verbose logging.')
def main(device_model_id, device_id, trigger, verbose):

    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)

    try:
        with HubAssistant(device_model_id, device_id) as hub_assistant:

            # Wait for trigger the first time.
            wait_for_trigger = True

            # Assist loop
            while True:
                if wait_for_trigger:
                    if trigger == "keystroke":
                        click.pause(info=('Presiona una tecla para activar '
                                        'el asistente...'))
                    else:
                        print('Di "Ok, Google" para activar el asistente...')
                        hub_assistant.wait_for_hot_word("ok google")
                keep_conversation = hub_assistant.assist()
                # Wait for trigger if there is no follow-up turn in the conversation.
                wait_for_trigger = not keep_conversation
    except Exception:
        logging.error("Error en asistente.", stack_info=True)

if __name__ == '__main__':
    main()
