import unittest
import mock
import os

import mock
from unittest import TestCase, skip
from hollowman import conf
from marathon import MarathonApp
import os

#from hollowman.conf import _build_cors_whitelist
import hollowman

class ConfTest(unittest.TestCase):

    def test_build_cors_whitelist(self):
        self.assertEqual([], hollowman.conf._build_cors_whitelist(""))
        self.assertEqual([], hollowman.conf._build_cors_whitelist(None))
        self.assertEqual(["name.com.br"], hollowman.conf._build_cors_whitelist("name.com.br"))
        self.assertEqual(["name.com.br", "other.com.br"], hollowman.conf._build_cors_whitelist("name.com.br,other.com.br"))
        self.assertEqual(["name.com.br", "other.com.br"], hollowman.conf._build_cors_whitelist("  name.com.br,  other.com.br  "))
        self.assertEqual(["name.com.br"], hollowman.conf._build_cors_whitelist("name.com.br,"))
        self.assertEqual(["name.com.br"], hollowman.conf._build_cors_whitelist(",name.com.br"))
