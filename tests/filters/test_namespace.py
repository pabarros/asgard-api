

import unittest


from hollowman.models import Account, User
from hollowman.marathonapp import SieveMarathonApp
from hollowman.filters.namespace import NameSpaceFilter
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

