import unittest

from typing import Optional

from valcheck.decorators import function_input_validator
from valcheck.exceptions import FunctionInputValidationException
from valcheck import fields
from valcheck.validators import Validator


class HelloValidator(Validator):
    x = fields.IntegerField()
    y = fields.FloatField()
    z = fields.IntegerStringField()
    a = fields.StringField(allow_empty=False)
    b = fields.DictionaryField(allow_empty=False)
    c = fields.ListField(allow_empty=False)
    d = fields.DictionaryField(allow_empty=False, required=False, nullable=True)


def hello_args_to_kwargs(*args):
    x, y, z = args
    return {
        "x": x,
        "y": y,
        "z": z,
    }


@function_input_validator(
    validator_model=HelloValidator,
    validator_model_kwargs=dict(context=None, deep_copy=False),
    args_to_kwargs=hello_args_to_kwargs,
)
def hello(x: int, y: float, z: str, /, *, a: str, b: dict, c: list, d: Optional[dict] = None) -> str:
    return "Hello"


class TestFunctionInputDecorator(unittest.TestCase):

    def test_valid_cases(self):
        expected_output = "Hello"

        self.assertEqual(
            hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"]),
            expected_output,
        )
        self.assertEqual(
            hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"], d=None),
            expected_output,
        )
        self.assertEqual(
            hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"], d={"key": "value"}),
            expected_output,
        )

    def test_invalid_cases(self):
        try:
            hello("1", "2.3", 3001, a=b"something", b=[{"key": "value"}], c=("something", ), d='{"key": "value"}')
        except FunctionInputValidationException as exc:
            self.assertTrue(
                exc.as_dict().get("error_count", 0) == 7,
            )
        else:
            self.assertTrue(
                False,
                msg="Expected the `valcheck.exceptions.FunctionInputValidationException` to be raised",
            )

