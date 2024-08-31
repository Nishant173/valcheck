## Writing validators with multiple inheritance

from pprint import pprint
from typing import List, Type

from valcheck import fields, models, validators


class ValidatorA(validators.Validator):
    a1 = fields.IntegerField()
    a2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("a1") >= self.get_validated_value("a2"):
            return [models.Error(description="a1 must be < a2", initial_field_path="a1/a2")]
        return []


class ValidatorB(validators.Validator):
    b1 = fields.IntegerField()
    b2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("b1") >= self.get_validated_value("b2"):
            return [models.Error(description="b1 must be < b2", initial_field_path="b1/b2")]
        return []


class ValidatorC(validators.Validator):
    c1 = fields.IntegerField()
    c2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("c1") >= self.get_validated_value("c2"):
            return [models.Error(description="c1 must be < c2", initial_field_path="c1/c2")]
        return []


class ValidatorX(ValidatorA, ValidatorB, ValidatorC):
    x1 = fields.IntegerField()
    x2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("x1") >= self.get_validated_value("x2"):
            return [models.Error(description="x1 must be < x2", initial_field_path="x1/x2")]
        return []

    def model_validators_to_ignore(self) -> List[Type[validators.Validator]]:
        return [ValidatorB]


if __name__ == "__main__":
    data = {
        "a1": 1,
        "a2": 2,
        "b1": 1,
        "b2": -2,
        "c1": 1,
        "c2": 2,
        "x1": 1,
        "x2": 2,
    }
    validator_instance = ValidatorX(data=data)
    print("\nField validators")
    pprint(validator_instance.list_field_validators())
    errors = validator_instance.run_validations()
    if errors:
        print("\nErrors")
        pprint([e.as_dict() for e in errors])
    else:
        print("\nValidated data")
        pprint(validator_instance.validated_data)
