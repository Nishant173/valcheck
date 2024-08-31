## Using Validator.extra_data property

from pprint import pprint

from valcheck import fields, validators


class SomeValidator(validators.Validator):
    a = fields.IntegerField()
    b = fields.IntegerField()
    c = fields.IntegerField()
    d = fields.IntegerField()


if __name__ == "__main__":
    data = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
        "f": 6,
    }
    val = SomeValidator(data=data)
    val.run_validations(raise_exception=True)

    print("Data")
    pprint(data)

    print("\n")
    print("Validated data")
    pprint(val.validated_data)

    print("\n")
    print("Extra data")
    pprint(val.extra_data)
