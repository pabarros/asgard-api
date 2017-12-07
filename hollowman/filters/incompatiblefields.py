

class IncompatibleFieldsFilter:
    """
    Esse filtro serve para corrigir alguns comportamentos do Marathon.
    Quando fazer GET em uma app, o marathon entrega um JSON que contém
    alguns campos que o próprio se recusa a receber, caso façamos um PUT/POST
    com esse JSON de volta pra ele.

    Um exmeplo de campo é o `ports`. Quando você pega uma app que tem portas definidas
    o JSON contém o campo `ports` preenchido com a lista de `container.docker.portMappings[].servicePort`
    O problema é que quando você tenta criar uma app com um JSON onde você tem ambos os campos:
        - port_definitions
        - ports

        O marathon recusa a criar a app, retornando o erro: "You cannot specify both ports and port definitions"
    """

    def write(self, user, request_app, original_app):
        """
        Método que altera uma app quando há uma escrita.
        """
        request_app.ports = []
        request_app.port_definitions = []
        return request_app

