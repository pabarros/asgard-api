from asynctest import TestCase

from asgard.models.base import ModelFactory, BaseModel


class BaseModelTest(TestCase):
    async def test_choose_instance_based_on_type_field(self):
        class BaseAgent(BaseModel):
            pass

        Agent = ModelFactory(BaseAgent)

        class ModelOne(BaseAgent):
            type: str = "ONE"
            other_field: str

        class ModelTwo(BaseAgent):
            type: str = "TWO"

        instance = Agent(**{"type": "ONE", "other_field": "value"})
        self.assertIsInstance(instance, ModelOne)
        self.assertDictEqual(
            {"type": "ONE", "other_field": "value", "errors": {}},
            instance.dict(),
        )
