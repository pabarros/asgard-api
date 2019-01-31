import os
import base64
import unittest
from mock import patch

from hollowman import conf


class ConfTest(unittest.TestCase):
    def test_build_cors_whitelist(self):
        self.assertEqual([], conf._build_cors_whitelist(""))
        self.assertEqual([], conf._build_cors_whitelist(None))
        self.assertEqual(
            ["name.com.br"], conf._build_cors_whitelist("name.com.br")
        )
        self.assertEqual(
            ["name.com.br", "other.com.br"],
            conf._build_cors_whitelist("name.com.br,other.com.br"),
        )
        self.assertEqual(
            ["name.com.br", "other.com.br"],
            conf._build_cors_whitelist("  name.com.br,  other.com.br  "),
        )
        self.assertEqual(
            ["name.com.br"], conf._build_cors_whitelist("name.com.br,")
        )
        self.assertEqual(
            ["name.com.br"], conf._build_cors_whitelist(",name.com.br")
        )

    def test_it_formats_auth_header(self):
        auth_type, auth_value = conf.MARATHON_AUTH_HEADER.split(" ")

        self.assertEqual(auth_type, "Basic")
        self.assertEqual(
            base64.b64decode(auth_value).decode("utf-8"),
            conf.MARATHON_CREDENTIALS,
        )

    def test_build_marathon_addresses_default_value(self):
        addresses = list(conf._build_marathon_addresses())
        self.assertEqual(1, len(addresses))
        self.assertEqual("http://127.0.0.1:8080", addresses[0])

    def test_build_marathon_addresses(self):
        """
        Certificamos que o código le corretamentee as envs passadas
        e monta a lista de endereços dos Marathons.
        """
        new_environ = {
            "HOLLOWMAN_MARATHON_ADDRESS": "http://127.0.0.1:8079",
            "HOLLOWMAN_MARATHON_ADDRESS_0": "http://127.0.0.1:8080",
            "HOLLOWMAN_MARATHON_ADDRESS_1": "http://127.0.0.2:8081",
            "HOLLOWMAN_MARATHON_ADDRESS_2": "http://127.0.0.3:8082",
        }
        with patch.multiple(os, environ=new_environ):
            addresses = list(conf._build_marathon_addresses())
            self.assertEqual(4, len(addresses))
            self.assertEqual("http://127.0.0.1:8079", addresses[0])
            self.assertEqual("http://127.0.0.1:8080", addresses[1])
            self.assertEqual("http://127.0.0.2:8081", addresses[2])
            self.assertEqual("http://127.0.0.3:8082", addresses[3])

    def test_build_marathon_addresses_no_repetition(self):
        new_environ = {
            "HOLLOWMAN_MARATHON_ADDRESS_0": "http://127.0.0.1:8080",
            "HOLLOWMAN_MARATHON_ADDRESS_1": "http://127.0.0.1:8080",
            "HOLLOWMAN_MARATHON_ADDRESS_2": "http://127.0.0.3:8082",
        }
        with patch.multiple(os, environ=new_environ):
            addresses = list(conf._build_marathon_addresses())
            self.assertEqual(2, len(addresses))
            self.assertEqual("http://127.0.0.1:8080", addresses[0])
            self.assertEqual("http://127.0.0.3:8082", addresses[1])

    def test_normalize_marathon_addresses(self):
        """
        Certifica que removemos a barra do final do endereço.
        Todas as barras, mesmo que existam múltiplas barras finais.
        """
        new_environ = {
            "HOLLOWMAN_MARATHON_ADDRESS_0": "http://127.0.0.1:8080",
            "HOLLOWMAN_MARATHON_ADDRESS_1": "http://127.0.0.2:8080/",
            "HOLLOWMAN_MARATHON_ADDRESS_2": "http://127.0.0.3:8082///",
        }
        with patch.multiple(os, environ=new_environ):
            addresses = list(conf._build_marathon_addresses())
            self.assertEqual(3, len(addresses))
            self.assertEqual("http://127.0.0.1:8080", addresses[0])
            self.assertEqual("http://127.0.0.2:8080", addresses[1])
            self.assertEqual("http://127.0.0.3:8082", addresses[2])
