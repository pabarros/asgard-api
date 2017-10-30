

import unittest
import json
from flask import Response as FlaskResponse
from marathon.models.group import MarathonGroup

from http import HTTPStatus


from hollowman.app import application
from hollowman.models import Account, User
from hollowman.marathonapp import SieveMarathonApp
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.http_wrappers.response import Response
from tests.utils import with_json_fixture

class TestNamespaceFilter(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = NameSpaceFilter()
        self.request_app = SieveMarathonApp.from_json(single_full_app_fixture)
        self.original_app = SieveMarathonApp.from_json(single_full_app_fixture)
        self.account = Account(name="Dev Account", namespace="dev", owner="company")
        self.user = User(tx_email="user@host.com.br")
        self.user.current_account = self.account

    def test_add_namespace_original_app_already_have_namespace(self):
        self.original_app.id = "/dev/foo"
        modified_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("/dev/foo", modified_app.id)

    def test_add_namespace_request_app_already_have_namespace(self):
        """
        Independente de qualquer coisa, temos *sempre* que adicionar
        o namespace ao request app. Isso evita que alguém consiga acessar
        uma app de outro namespace.
        """
        self.original_app.id = "/dev/foo"
        self.request_app.id = "/dev/foo"
        modified_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("/dev/dev/foo", modified_app.id)

    def test_do_not_add_namespace_if_original_app_does_not_already_have_it(self):
        """
        Durante o periodo de migração, o filtro não vaai mexer em apps que ainda não foram
        migradas. Antes de convidar alguém para usar nosso sistema, todas as apps da sieve precisam
        ser migradas para `/sieve`
        """
        modified_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("/foo", modified_app.id)

    def test_add_namespace_create_new_app(self):
        """
        Para novas apps, sempre vamos adicionar o prefixo.
        """
        modified_app = self.filter.write(self.user, self.request_app, SieveMarathonApp())
        self.assertEqual("/dev/foo", modified_app.id)

    def test_does_nothing_if_user_is_none(self):
        modified_app = self.filter.write(None, self.request_app, SieveMarathonApp())
        self.assertEqual("/foo", modified_app.id)

    def test_response_remove_namespace_if_original_app_already_have_namespace(self):
        self.original_app.id = "/dev/foo"
        modified_app = self.filter.response(self.user, self.request_app, self.original_app)
        self.assertEqual("/foo", modified_app.id)

    def test_response_does_nothing_if_user_is_none(self):
        self.request_app.id = "/dev/foo"
        modified_app = self.filter.response(None, self.request_app, SieveMarathonApp())
        self.assertEqual("/dev/foo", modified_app.id)

    def test_remove_namspace_from_string(self):
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/dev"))
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/dev/"))
        self.assertEqual("/foo/bar", self.filter._remove_namespace(self.user, "/dev/foo/bar"))
        self.assertEqual("/infra/foo", self.filter._remove_namespace(self.user, "/infra/foo"))
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/"))

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_group_name(self, group_dev_namespace_fixture):
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][1])
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.groups))
            # Não removemos o namespace de subgrupos.
            self.assertEqual("/dev/group-b/group-b0", filtered_group.groups[0].id)

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_app_name(self, group_dev_namespace_fixture):
        """
        Devemos remover o namespace de todas as apps to grupo.
        Mas não das apps dos subgrupos
        """
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][1])
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.apps))
            self.assertEqual("/group-b/appb0", filtered_group.apps[0].id)
