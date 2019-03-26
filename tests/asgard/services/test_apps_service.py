from asynctest import TestCase, skip


@skip("Future")
class AppsServiceTest(TestCase):
    async def test_calls_backend_with_correct_parameters(self):
        self.fail()
