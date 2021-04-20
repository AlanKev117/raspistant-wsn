import logging

from rpyc.utils.registry import REGISTRY_PORT, DEFAULT_PRUNING_TIMEOUT
from rpyc.utils.registry import UDPRegistryServer
from rpyc.lib import setup_logger
import click

@click.command()
@click.option('--port', '-p', default=REGISTRY_PORT,
            metavar='<puerto>', show_default=True,
            help='Puerto por el que el servidor recibe registros de servicios')
@click.option('--pruning-timeout', '-t', default=5,
            metavar='<segundos>', show_default=True,
            help=("Tiempo que se mantiene registrado un servicio después de "
                  "estar inactivo."))
@click.option('--verbose', '-v',
              is_flag=True,
              help="Se activa el modo verbose.")
def main(port, pruning_timeout, verbose):
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)
    registry_server(port, pruning_timeout)

def registry_server(port, pruning_timeout):
    logging.info("Servidor de registro iniciado.")
    server = UDPRegistryServer(port=port, pruning_timeout=pruning_timeout)
    server.start()

if __name__ == "__main__":
    main()
