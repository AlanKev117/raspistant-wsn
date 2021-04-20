class AssistantDisconnectedError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class RepeatedNodeNameError(Exception):
    def __init__(self, node_name):
        self.repeated_name = node_name

    def __str__(self):
        return f"Nombre de nodo repetido: {self.repeated_name}"
