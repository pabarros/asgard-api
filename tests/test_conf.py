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
