# Copyright 2021 Alan Fuentes
# Copyright 2021 Yael Estrada
# Copyright 2021 Noé Acosta

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Servidor de Registro

  En este código se implementa el servidor de registro que se encargará
  de recibir los nodos sensores disponibles para ser descubiertos con el
  asistente.

"""
import logging

import click

from rpyc.utils.registry import REGISTRY_PORT
from rpyc.utils.registry import UDPRegistryServer


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
    """ Funcion generadora del servidor de registro.

    Esta función tiene como objetivo iniciar el servidor de registro
    al ser invocada como un hilo del programa raspistant.py.

    Args:
        port:
            Puerto por el que el servidor recibe registros de servicios.
        pruning_timeout:
            Tiempo en que se mantiene registrado un servicio despues de 
            estar inactivo
        verbose:
            Define el comportamiento de los logs.
    """

    # Creación de logger para servidor de registro
    logger = logging.getLogger(f"REGSRV/UDP/{port}")
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)

    # Creación e invocación de servidor de registro
    server = UDPRegistryServer(port=port,
                               pruning_timeout=pruning_timeout,
                               logger=logger)
    server.start()


if __name__ == "__main__":
    main()
