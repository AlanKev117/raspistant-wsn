import logging

from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT
from rpyc.utils.registry import UDPRegistryServer
from rpyc.lib import setup_logger
import click

@click.command()
@click.option('--port', default=REGISTRY_PORT,
            metavar='<puerto>', show_default=True,
            help='Puerto por el que el servidor recibe registros de servicios')
@click.option('--pruning-timeout', default=DEFAULT_PRUNING_TIMEOUT,
            metavar='<segundos>', show_default=True,
            help="""Tiempo que se mantiene registrado un servicio después de 
                 que deja de enviar paquetes de registro o que se desactiva.""")
def main(port, pruning_timeout):
    registry_server(port, pruning_timeout)

def registry_server(port, pruning_timeout):
    print("Servidor de registro iniciado.")
    server = UDPRegistryServer(port=port, pruning_timeout=pruning_timeout)
    # Muestra todos los logs, logger por defecto es stderr
    setup_logger(False, None)
    server.start()

if __name__ == "__main__":
    main()
