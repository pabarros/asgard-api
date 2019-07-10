from asynctest import TestCase
from pydantic import ValidationError

from asgard.models.spec.constraint import ConstraintSpec, ConstraintOperator


class ConstraintSpecModelTest(TestCase):
    async def test_constraint_spec_model_from_dict(self):
        constraint = ConstraintSpec(
            **{
                "type": "ASGARD",
                "label": "workload",
                "operator": "LIKE",
                "value": "general",
            }
        )
        self.assertEqual("workload", constraint.label)
        self.assertEqual("general", constraint.value)
        self.assertEqual(ConstraintOperator.LIKE, constraint.operator)

    async def test_constraint_spec_model_from_dict_validate_invalid_operator(
        self
    ):
        try:
            ConstraintSpec(
                **{
                    "type": "ASGARD",
                    "label": "workload",
                    "operator": "OTHER",
                    "value": "general",
                }
            )
        except ValidationError as e:
            self.assertEqual(1, len(e.errors()))
            self.assertEqual(
                {
                    "loc": ("operator",),
                    "msg": "value is not a valid enumeration member",
                    "type": "type_error.enum",
                },
                e.errors()[0],
            )

    async def test_serialize_constraint_spec_model(self):
        constraint = ConstraintSpec(
            label="workload", operator=ConstraintOperator.LIKE, value="general"
        )
        self.assertEqual(
            {
                "type": "ASGARD",
                "label": "workload",
                "operator": ConstraintOperator.LIKE.value,
                "value": "general",
            },
            constraint.dict(),
        )
