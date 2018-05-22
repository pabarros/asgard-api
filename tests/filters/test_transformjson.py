import unittest

class TransformJSONTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_is_json_new_format(self):
        """
        Confirma que conseguimos reconhecer um JSON já no formato novo
        Formato novo contém as chaves:
            * `networks`
            * `container.portMappings`
        """
        self.fail()

    def test_transform_json_network_already_new_format_before_upstream_request(self):
        """
        Não fazemos nada se o JSON já estiver no formato novo, ou seja, com a chave `networks` (na raiz).
        """
        self.fail()

    def test_transform_json_change_network_before_upstream_request(self):
        """
        Movemos o dict de `container.docker.network` para `netowks`
        """
        self.fail()

    def test_transform_json_change_port_mappings_already_new_format_before_upstream_request(self):
        """
        Não fazemos nada se o JSON já possui a key `container.portMappings`
        """
        self.fail()

    def test_transform_json_change_port_mappings_before_upstream_request(self):
        """
        Movemos `container.docker.portMappings` para `container.portMappings`
        """
        self.fail()

    def test_transform_json_change_network_already_new_format_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_network_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_port_mappings_already_new_format_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_port_mappings_before_response_to_client(self):
        self.fail()

