from asynctest import TestCase


class AppsBackendTest(TestCase):
    async def test_apps_app_not_found(self):
        self.fail()

    async def test_apps_get_app_from_another_account(self):
        """
        Talvez esse teste não faça sentido pois o parametro Account já "trava" que o app tenha que ser dessa Account
        """
        self.fail()

    async def test_get_existant_app(self):
        self.fail()
