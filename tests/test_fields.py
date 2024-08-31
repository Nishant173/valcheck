from typing import Any, Dict, List, Type
import unittest

from valcheck import fields, models, validators


DATE_FORMAT = "%d %B, %Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"
CHOICES = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
)


def has_errors(errors: List[models.Error], /) -> bool:
    return bool(errors)


class BooleanFieldValidator(validators.Validator):
    boolean_field = fields.BooleanField()


class StringFieldValidator(validators.Validator):
    string_field = fields.StringField()


class JsonStringFieldValidator(validators.Validator):
    json_string_field = fields.JsonStringField()


class EmailIdFieldValidator(validators.Validator):
    email_id_field = fields.EmailIdField()


class UuidStringFieldValidator(validators.Validator):
    uuid_string_field = fields.UuidStringField()


class DateStringValidator(validators.Validator):
    date_string_field = fields.DateStringField(format_=DATE_FORMAT)


class DatetimeStringValidator(validators.Validator):
    datetime_string_field = fields.DatetimeStringField(format_=DATETIME_FORMAT)


class ChoiceFieldValidator(validators.Validator):
    choice_field = fields.ChoiceField(choices=CHOICES)


class MultiChoiceFieldValidator(validators.Validator):
    multi_choice_field = fields.MultiChoiceField(choices=CHOICES)


class BytesFieldValidator(validators.Validator):
    bytes_field = fields.BytesField()


class NumberFieldValidator(validators.Validator):
    number_field = fields.NumberField()


class IntegerFieldValidator(validators.Validator):
    integer_field = fields.IntegerField()


class FloatFieldValidator(validators.Validator):
    float_field = fields.FloatField()


class NumberStringFieldValidator(validators.Validator):
    number_string_field = fields.NumberStringField()


class IntegerStringFieldValidator(validators.Validator):
    integer_string_field = fields.IntegerStringField()


class FloatStringFieldValidator(validators.Validator):
    float_string_field = fields.FloatStringField()


class DictionaryFieldValidator(validators.Validator):
    dictionary_field = fields.DictionaryField()


class ListFieldValidator(validators.Validator):
    list_field = fields.ListField()


class TestField(unittest.TestCase):

    def assert_validations(
            self,
            *,
            validator_model: Type[validators.Validator],
            io: List[Dict[str, Any]],
        ) -> None:
        """Helper method that checks if the inputs passed to the given `validator_model` are valid"""
        for item in io:
            data: Dict[str, Any] = item["data"]
            should_be_valid: bool = item["should_be_valid"]
            val = validator_model(data=data)
            val.run_validations()
            errors = val.errors
            message = {
                "validator_model": validator_model.__name__,
                "data": data,
                "should_be_valid": should_be_valid,
                "errors": [error.as_dict() for error in errors],
                "is_valid": not has_errors(errors),
            }
            if should_be_valid:
                self.assertTrue(
                    expr=not has_errors(errors),
                    msg=message,
                )
            else:
                self.assertTrue(
                    expr=has_errors(errors),
                    msg=message,
                )

    def test_boolean_field(self):
        self.assert_validations(
            validator_model=BooleanFieldValidator,
            io=[
                {
                    "data": {"boolean_field": True},
                    "should_be_valid": True,
                },
                {
                    "data": {"boolean_field": False},
                    "should_be_valid": True,
                },
                {
                    "data": {"boolean_field": None},
                    "should_be_valid": False,
                },
                {
                    "data": {"boolean_field": 1},
                    "should_be_valid": False,
                },
                {
                    "data": {"boolean_field": 0},
                    "should_be_valid": False,
                },
            ],
        )

    def test_string_field(self):
        self.assert_validations(
            validator_model=StringFieldValidator,
            io=[
                {
                    "data": {"string_field": "hello"},
                    "should_be_valid": True,
                },
                {
                    "data": {"string_field": ""},
                    "should_be_valid": True,
                },
                {
                    "data": {"string_field": None},
                    "should_be_valid": False,
                },
            ],
        )

    def test_json_string_field(self):
        self.assert_validations(
            validator_model=JsonStringFieldValidator,
            io=[
                {
                    "data": {"json_string_field": '{"key1": "value1", "key2": "value2", "key3": [1, 2, 3, null]}'},
                    "should_be_valid": True,
                },
                {
                    "data": {"json_string_field": '[1, 2, 3, null]'},
                    "should_be_valid": True,
                },
                {
                    "data": {"json_string_field": None},
                    "should_be_valid": False,
                },
            ],
        )

    def test_email_id_field(self):
        self.assert_validations(
            validator_model=EmailIdFieldValidator,
            io=[
                {
                    "data": {"email_id_field": "hello@example.com"},
                    "should_be_valid": True,
                },
                {
                    "data": {"email_id_field": "hello@example.com."},
                    "should_be_valid": False,
                },
                {
                    "data": {"email_id_field": ""},
                    "should_be_valid": False,
                },
            ],
        )

    def test_uuid_string_field(self):
        self.assert_validations(
            validator_model=UuidStringFieldValidator,
            io=[
                {
                    "data": {"uuid_string_field": "09179144-e336-4797-a957-8640ac9ba367"},
                    "should_be_valid": True,
                },
                {
                    "data": {"uuid_string_field": "09179144e3364797a9578640ac9ba367"},
                    "should_be_valid": False,
                },
                {
                    "data": {"uuid_string_field": "09179144-e336-4797-a957-8640ac9ba367 "},
                    "should_be_valid": False,
                },
                {
                    "data": {"uuid_string_field": "09179144-e336-4797-a957-8640ac9ba367."},
                    "should_be_valid": False,
                },
            ],
        )

    def test_date_string_field(self):
        self.assert_validations(
            validator_model=DateStringValidator,
            io=[
                {
                    "data": {"date_string_field": "01 January, 2020"},
                    "should_be_valid": True,
                },
                {
                    "data": {"date_string_field": "01 January 2020"},
                    "should_be_valid": False,
                },
                {
                    "data": {"date_string_field": "01 January 2020 17:45:00"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_datetime_string_field(self):
        self.assert_validations(
            validator_model=DatetimeStringValidator,
            io=[
                {
                    "data": {"datetime_string_field": "2020-05-25 17:30:00 +0530"},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field": "2020-05-25 17:30:00+0530"},
                    "should_be_valid": False,
                },
                {
                    "data": {"datetime_string_field": "2020-05-25 17:30:00"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_choice_field(self):
        self.assert_validations(
            validator_model=ChoiceFieldValidator,
            io=[
                {
                    "data": {"choice_field": "A"},
                    "should_be_valid": True,
                },
                {
                    "data": {"choice_field": "F"},
                    "should_be_valid": True,
                },
                {
                    "data": {"choice_field": "G"},
                    "should_be_valid": False,
                },
                {
                    "data": {"choice_field": "Z"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_multi_choice_field(self):
        self.assert_validations(
            validator_model=MultiChoiceFieldValidator,
            io=[
                {
                    "data": {"multi_choice_field": CHOICES},
                    "should_be_valid": True,
                },
                {
                    "data": {"multi_choice_field": ["A", "C", "E"]},
                    "should_be_valid": True,
                },
                {
                    "data": {"multi_choice_field": ["B", "D", "F"]},
                    "should_be_valid": True,
                },
                {
                    "data": {"multi_choice_field": ["G", "H"]},
                    "should_be_valid": False,
                },
                {
                    "data": {"multi_choice_field": ["G"]},
                    "should_be_valid": False,
                },
                {
                    "data": {"multi_choice_field": []},
                    "should_be_valid": False,
                },
            ],
        )
    
    def test_bytes_field(self):
        self.assert_validations(
            validator_model=BytesFieldValidator,
            io=[
                {
                    "data": {"bytes_field": b"hello"},
                    "should_be_valid": True,
                },
                {
                    "data": {"bytes_field": b""},
                    "should_be_valid": True,
                },
                {
                    "data": {"bytes_field": "".encode()},
                    "should_be_valid": True,
                },
                {
                    "data": {"bytes_field": "hello"},
                    "should_be_valid": False,
                },
                {
                    "data": {"bytes_field": ""},
                    "should_be_valid": False,
                },
            ],
        )

    def test_number_field(self):
        self.assert_validations(
            validator_model=NumberFieldValidator,
            io=[
                {
                    "data": {"number_field": 0},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_field": 0.01},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_field": -0.01},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_field": 1},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_field": -1},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_field": "1"},
                    "should_be_valid": False,
                },
                {
                    "data": {"number_field": "-1"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_integer_field(self):
        self.assert_validations(
            validator_model=IntegerFieldValidator,
            io=[
                {
                    "data": {"integer_field": 0},
                    "should_be_valid": True,
                },
                {
                    "data": {"integer_field": 0.01},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_field": -0.01},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_field": 1},
                    "should_be_valid": True,
                },
                {
                    "data": {"integer_field": -1},
                    "should_be_valid": True,
                },
                {
                    "data": {"integer_field": "1"},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_field": "-1"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_float_field(self):
        self.assert_validations(
            validator_model=FloatFieldValidator,
            io=[
                {
                    "data": {"float_field": 0},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_field": 0.01},
                    "should_be_valid": True,
                },
                {
                    "data": {"float_field": -0.01},
                    "should_be_valid": True,
                },
                {
                    "data": {"float_field": 1},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_field": -1},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_field": "1"},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_field": "-1"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_number_string_field(self):
        self.assert_validations(
            validator_model=NumberStringFieldValidator,
            io=[
                {
                    "data": {"number_string_field": 0},
                    "should_be_valid": False,
                },
                {
                    "data": {"number_string_field": 0.01},
                    "should_be_valid": False,
                },
                {
                    "data": {"number_string_field": "0.01"},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_string_field": 1},
                    "should_be_valid": False,
                },
                {
                    "data": {"number_string_field": -1},
                    "should_be_valid": False,
                },
                {
                    "data": {"number_string_field": "1"},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_string_field": "-1"},
                    "should_be_valid": True,
                },
            ],
        )

    def test_integer_string_field(self):
        self.assert_validations(
            validator_model=IntegerStringFieldValidator,
            io=[
                {
                    "data": {"integer_string_field": 0},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_string_field": 0.01},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_string_field": "0.01"},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_string_field": 1},
                    "should_be_valid": False,
                },
                {
                    "data": {"integer_string_field": "1"},
                    "should_be_valid": True,
                },
                {
                    "data": {"integer_string_field": "-1"},
                    "should_be_valid": True,
                },
            ],
        )

    def test_float_string_field(self):
        self.assert_validations(
            validator_model=FloatStringFieldValidator,
            io=[
                {
                    "data": {"float_string_field": 0},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_string_field": 0.01},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_string_field": "0.01"},
                    "should_be_valid": True,
                },
                {
                    "data": {"float_string_field": 1},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_string_field": "1"},
                    "should_be_valid": False,
                },
                {
                    "data": {"float_string_field": "-1.01"},
                    "should_be_valid": True,
                },
            ],
        )

    def test_dictionary_field(self):
        self.assert_validations(
            validator_model=DictionaryFieldValidator,
            io=[
                {
                    "data": {"dictionary_field": {}},
                    "should_be_valid": True,
                },
                {
                    "data": {"dictionary_field": {"a": 1, "b": 2}},
                    "should_be_valid": True,
                },
                {
                    "data": {"dictionary_field": dict(a=1, b=2)},
                    "should_be_valid": True,
                },
                {
                    "data": {"dictionary_field": {"hello", "world"}},
                    "should_be_valid": False,
                },
                {
                    "data": {"dictionary_field": "{}"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_list_field(self):
        self.assert_validations(
            validator_model=ListFieldValidator,
            io=[
                {
                    "data": {"list_field": []},
                    "should_be_valid": True,
                },
                {
                    "data": {"list_field": ["a", "b", "c", "d"]},
                    "should_be_valid": True,
                },
                {
                    "data": {"list_field": list("abcd")},
                    "should_be_valid": True,
                },
                {
                    "data": {"list_field": "[]"},
                    "should_be_valid": False,
                },
            ],
        )

