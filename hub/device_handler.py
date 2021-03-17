from googlesamples.assistant.grpc.pushtotalk import device_helpers

def hub_device_handler_creator(device_id):
    hub_device_handler = device_helpers.DeviceRequestHandler(device_id)

    @hub_device_handler.command('action.devices.commands.OnOff')
    def onoff(on):
        if on:
            logging.info('Turning device on')
        else:
            logging.info('Turning device off')

    @hub_device_handler.command('com.example.commands.BlinkLight')
    def blink(speed, number):
        logging.info('Blinking device %s times.' % number)
        delay = 1
        if speed == "SLOWLY":
            delay = 2
        elif speed == "QUICKLY":
            delay = 0.5
        for i in range(int(number)):
            logging.info('Device is blinking.')
            time.sleep(delay)
    
    return hub_device_handler