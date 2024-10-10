## Using `valcheck.decorators.function_input_validator`

from typing import Optional

from valcheck.decorators import function_input_validator
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
def hello(x: int, y: float, z: str, /, *, a: str, b: dict, c: list, d: Optional[dict] = None) -> None:
    print("Hello")


def main():
    hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"])
    hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"], d=None)
    hello(1, 2.3, "3001", a="something", b={"key": "value"}, c=["something"], d={"key": "value"})


if __name__ == "__main__":
    main()


