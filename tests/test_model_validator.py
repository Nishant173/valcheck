from typing import List, Type
import unittest

from valcheck import fields, models, validators


class ValidatorA(validators.Validator):
    a1 = fields.IntegerField()
    a2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("a1") >= self.get_validated_value("a2"):
            return [models.Error(description="a1 must be < a2", field_path_part="a1/a2")]
        return []


class ValidatorB(validators.Validator):
    b1 = fields.IntegerField()
    b2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("b1") >= self.get_validated_value("b2"):
            return [models.Error(description="b1 must be < b2", field_path_part="b1/b2")]
        return []


class ValidatorC(validators.Validator):
    c1 = fields.IntegerField()
    c2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("c1") >= self.get_validated_value("c2"):
            return [models.Error(description="c1 must be < c2", field_path_part="c1/c2")]
        return []


class ValidatorX(ValidatorA, ValidatorB, ValidatorC):
    x1 = fields.IntegerField()
    x2 = fields.IntegerField()

    def model_validator(self) -> List[models.Error]:
        if self.get_validated_value("x1") >= self.get_validated_value("x2"):
            return [models.Error(description="x1 must be < x2", field_path_part="x1/x2")]
        return []

    def model_validators_to_consider(self) -> List[Type[validators.Validator]]:
        return [ValidatorA, ValidatorB, ValidatorC]


class TestModelValidator(unittest.TestCase):

    def test_model_validator_hierarchy(self):
        data = {
            "a1": 3,
            "a2": 2,
            "b1": 3,
            "b2": 2,
            "c1": 3,
            "c2": 2,
            "x1": 3,
            "x2": 2,
        }
        val = ValidatorX(data=data)
        val.run_validations()
        # count of errors must be 4, since all the `model_validator()` calls in the hierarchy (of 4 classes) fail once for each class
        self.assertTrue(len(val.errors) == 4)
