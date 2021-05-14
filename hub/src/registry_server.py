import logging

from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.registry import UDPRegistryServer
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
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)
    registry_server(port, pruning_timeout, verbose)


def registry_server(port, pruning_timeout, verbose=False):

    # Creación de logger para servidor de registro
    logger = logging.getLogger(f"REGSRV/UDP/{port}")
    h = logging.StreamHandler()
    f = logging.Formatter("%(levelname)s:%(name)s:%(msg)s")
    h.setFormatter(f)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)

    # Creación e invocación de servidor de registro
    server = UDPRegistryServer(port=port,
                               pruning_timeout=pruning_timeout,
                               logger=logger)
    server.start()



if __name__ == "__main__":
    main()
