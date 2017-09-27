from unittest import TestCase
from unittest.mock import patch

from marathon import MarathonApp

from hollowman.app import application
from hollowman.request_handlers import new


class RequestHandlersTests(TestCase):
    def setUp(self):
        parser_patch = patch('hollowman.request_handlers.RequestParser')
        self.parser = parser_patch.start()
        self.parser.return_value.is_group_request.return_value = False

        self.request_apps = [
            (MarathonApp(id='/xablau'), MarathonApp(id='/xena')),
            (MarathonApp(id='/foo'), MarathonApp(id='/bar')),
        ]
        self.parser.return_value.split.return_value = self.request_apps

        dispatch_patch = patch('hollowman.request_handlers.dispatch',
                               side_effect=lambda *args, **kwargs: kwargs['request_app'])
        self.dispatch = dispatch_patch.start()

    def tearDown(self):
        patch.stopall()

    def test_it_dispatches_apps_from_request(self):
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            with patch('hollowman.request_handlers.old') as old:
                response = new(ctx.request)

                self.assertEqual(response, old.return_value)
                self.parser.return_value.split.assert_called_once()
                self.parser.return_value.join.assert_called_once_with(self.request_apps)
