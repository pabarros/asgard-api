from unittest.mock import patch

from flask import Response
from tests import rebuild_schema

import hollowman
from asgard.models.account import AccountDB as Account
from hollowman.models import HollowmanSession, User


class BaseApiTests:
    user_tx_authkey = "69ed620926be4067a36402c3f7e9ddf0"

    def setUp(self):
        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey=self.user_tx_authkey,
        )
        self.account_dev = Account(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.user.accounts = [self.account_dev]
        self.user.current_account = self.account_dev
        self.session.add(self.account_dev)
        self.session.add(self.user)
        self.session.commit()

        self.proxy_mock_patcher = patch.object(hollowman.routes, "raw_proxy")
        self.proxy_mock = self.proxy_mock_patcher.start()
        self.proxy_mock.return_value = Response(status=200)

    @property
    def auth_header(self):
        return {"Authorization": f"Token {self.user_tx_authkey}"}

    def tearDown(self):
        patch.stopall()
