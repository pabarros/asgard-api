
<<<<<<< HEAD
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

class TestConf(TestCase):

    def test_get_filter_env_variable_name(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'
        self.assertEqual(
            conf.ConfHelper.get_filter_env_variable_name(mocked_filter),
            'hollowman_foo'
        )

    def test_get_filter_env_variable_name_different_env(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        with mock.patch('hollowman.conf.variable_namespace', new_callable=mock.PropertyMock(return_value='bar')):
            self.assertEqual(
                conf.ConfHelper.get_filter_env_variable_name(mocked_filter, ['abcd']),
                'bar_foo_abcd'
            )

    def test_get_filter_label_variable_name(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'
        self.assertEqual(
            conf.ConfHelper.get_filter_label_variable_name(mocked_filter),
            'hollowman.foo'
        )

    def test_get_filter_label_variable_name_different_env(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        mocked_prop = mock.PropertyMock(return_value='bar')

        with mock.patch('hollowman.conf.variable_namespace', new_callable=mocked_prop):
            self.assertEqual(
                conf.ConfHelper.get_filter_label_variable_name(mocked_filter, ['abcd']),
                'bar.foo.abcd'
            )

    def test_is_filter_globally_enabled(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        self.assertTrue(conf.ConfHelper.is_filter_globally_enabled(mocked_filter))

    def test_is_filter_globally_disabled(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        envmock = mock.PropertyMock(return_value={'hollowman_foo_disable':'1'})

        with mock.patch.object(conf.ConfHelper, 'envvars', new_callable=envmock) as mocked_envvars:
            self.assertFalse(conf.ConfHelper.is_filter_globally_enabled(mocked_filter))

    def test_is_filter_locally_enabled(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        mocked_marathon_app = MarathonApp(None)

        self.assertTrue(conf.ConfHelper.is_filter_locally_enabled(
            mocked_filter,
            mocked_marathon_app
        ))

    def test_is_filter_locally_disabled(self):
        mocked_filter = mock.MagicMock()
        mocked_filter.name = 'foo'

        mocked_marathon_app = MarathonApp(None)
        mocked_marathon_app.labels['hollowman.foo.disable'] = '1'

        self.assertFalse(conf.ConfHelper.is_filter_locally_enabled(
            mocked_filter,
            mocked_marathon_app
        ))
