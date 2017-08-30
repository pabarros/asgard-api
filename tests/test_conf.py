import base64
import unittest

from hollowman import conf


class ConfTest(unittest.TestCase):

    def test_build_cors_whitelist(self):
        self.assertEqual([], conf._build_cors_whitelist(""))
        self.assertEqual([], conf._build_cors_whitelist(None))
        self.assertEqual(["name.com.br"], conf._build_cors_whitelist("name.com.br"))
        self.assertEqual(["name.com.br", "other.com.br"], conf._build_cors_whitelist("name.com.br,other.com.br"))
        self.assertEqual(["name.com.br", "other.com.br"], conf._build_cors_whitelist("  name.com.br,  other.com.br  "))
        self.assertEqual(["name.com.br"], conf._build_cors_whitelist("name.com.br,"))
        self.assertEqual(["name.com.br"], conf._build_cors_whitelist(",name.com.br"))

    def test_it_formats_auth_header(self):
        auth_type, auth_value = conf.MARATHON_AUTH_HEADER.split(" ")

        self.assertEqual(auth_type, 'Basic')
        self.assertEqual(base64.b64decode(auth_value).decode('utf-8'),
                         conf.MARATHON_CREDENTIALS)
