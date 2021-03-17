# raspistant-wsn

Una red de sensores inalámbricos alimentada por Google Assistant embebido en Raspberry Pi

* El directorio `hub/` contiene un proyecto en Python 3.5 con una continuación de la guía de incrustación de Google Assistant en dispositivos.

    1. Para ejecutarlo, prepare su dispositivo siguiendo la guía del sitio oficial de [Google Developers](https://developers.google.com/assistant/sdk/guides/service/python)
    1. Ejecute el archivo principal con el siguiente comando:
    ```bash
    python raspistant.py
    ```

* El directorio `sensor_node/` contiene un proyecto en Python 3.5 con el programa que correrá el nodo sensor para cualquier tipo de magnitud física.