from datetime import datetime, date, timezone
from typing import Any, Dict, List, Type
import unittest
import uuid

from valcheck import fields, models, utils, validators


DATE_FORMAT = "%d %B, %Y"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %z"
DATETIME_FORMAT_TZ_NAIVE = "%Y-%m-%d %H:%M:%S"
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


class FieldConversionValidator(validators.Validator):
    json_string_field_1 = fields.JsonStringField(which="JSON_OBJECT", to_python_obj=False)
    json_string_field_2 = fields.JsonStringField(which="JSON_OBJECT", to_python_obj=True)
    uuid_string_field_1 = fields.UuidStringField(to_uuid_obj=False)
    uuid_string_field_2 = fields.UuidStringField(to_uuid_obj=True)
    date_string_field_1 = fields.DateStringField(to_date_obj=False)
    date_string_field_2 = fields.DateStringField(to_date_obj=True)
    datetime_string_field_1 = fields.DatetimeStringField(to_datetime_obj=False)
    datetime_string_field_2 = fields.DatetimeStringField(to_datetime_obj=True)
    number_string_field_1 = fields.NumberStringField(to_number=False)
    number_string_field_2 = fields.NumberStringField(to_number=True)
    integer_string_field_1 = fields.IntegerStringField(to_integer=False)
    integer_string_field_2 = fields.IntegerStringField(to_integer=True)
    float_string_field_1 = fields.FloatStringField(to_float=False)
    float_string_field_2 = fields.FloatStringField(to_float=True)


class AnyFieldValidator1(validators.Validator):
    any_field_1 = fields.AnyField()


class AnyFieldValidator2(validators.Validator):
    any_field_2 = fields.AnyField(required=False, nullable=True)


class BooleanFieldValidator(validators.Validator):
    boolean_field = fields.BooleanField()


class StringFieldValidator(validators.Validator):
    string_field = fields.StringField()


class JsonStringFieldValidator(validators.Validator):
    json_string_field = fields.JsonStringField()


class EmailIdStringFieldValidator(validators.Validator):
    email_id_string_field = fields.EmailIdStringField()


class UuidStringFieldValidator(validators.Validator):
    uuid_string_field = fields.UuidStringField()


class UuidFieldValidator(validators.Validator):
    uuid_field = fields.UuidField()


class DateStringValidator(validators.Validator):
    date_string_field = fields.DateStringField(format_=DATE_FORMAT)


class DateValidator(validators.Validator):
    date_field = fields.DateField()


class DatetimeStringValidator(validators.Validator):
    datetime_string_field = fields.DatetimeStringField(format_=DATETIME_FORMAT)


class DatetimeStringValidatorV2(validators.Validator):
    datetime_string_field_tz_aware_v2 = fields.DatetimeStringField(
        format_=DATETIME_FORMAT,
        allowed_tz_names=["UTC", "UTC+05:30"],
        required=False,
    )
    datetime_string_field_tz_naive_v2 = fields.DatetimeStringField(
        format_=DATETIME_FORMAT_TZ_NAIVE,
        required=False,
    )


class DatetimeValidator(validators.Validator):
    datetime_field_tz_aware = fields.DatetimeField(timezone_aware=True, required=False)
    datetime_field_tz_naive = fields.DatetimeField(timezone_aware=False, required=False)


class DatetimeValidatorV2(validators.Validator):
    datetime_field_tz_aware_v2 = fields.DatetimeField(
        timezone_aware=True,
        allowed_tz_names=["UTC", "UTC+05:30"],
        required=False,
    )
    datetime_field_tz_naive_v2 = fields.DatetimeField(
        timezone_aware=False,
        required=False,
    )


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


class FieldParamsValidator(validators.Validator):
    five_letter_word = fields.StringField(
        allow_empty=False,
        source="five_letter_word_source",
        target="five_letter_word_target",
        required=False,
        nullable=True,
        default_factory=lambda: "hello",
        converter_factory=lambda value: value.upper() if isinstance(value, str) else None,
        validators=[
            lambda value: len(value) == 5,
            lambda value: all((char.islower() for char in value)),
        ],
        error=models.Error(
            description="The given custom string field is invalid. Must contain exactly 5 lower-case characters",
        ),
        type_alias="CustomStringField",
    )


class TestField(unittest.TestCase):

    def test_field_conversions(self):
        data = {
            "json_string_field_1": '{"key1": "value1", "key2": "value2"}',
            "json_string_field_2": '{"key1": "value1", "key2": "value2"}',
            "uuid_string_field_1": "ca2f7082-1b87-4324-b2c5-a3f624ca2eae",
            "uuid_string_field_2": "ca2f7082-1b87-4324-b2c5-a3f624ca2eae",
            "date_string_field_1": "2020-05-25",
            "date_string_field_2": "2020-05-25",
            "datetime_string_field_1": "2020-05-25 17:45:30.0+0000",
            "datetime_string_field_2": "2020-05-25 17:45:30.0+0000",
            "number_string_field_1": "3.1428",
            "number_string_field_2": "3.1428",
            "integer_string_field_1": "9015",
            "integer_string_field_2": "9015",
            "float_string_field_1": "3.1428",
            "float_string_field_2": "3.1428",
        }
        expected_validated_data = {
            "json_string_field_1": '{"key1": "value1", "key2": "value2"}',
            "json_string_field_2": {"key1": "value1", "key2": "value2"},
            "uuid_string_field_1": "ca2f7082-1b87-4324-b2c5-a3f624ca2eae",
            "uuid_string_field_2": uuid.UUID("ca2f7082-1b87-4324-b2c5-a3f624ca2eae"),
            "date_string_field_1": "2020-05-25",
            "date_string_field_2": date(year=2020, month=5, day=25),
            "datetime_string_field_1": "2020-05-25 17:45:30.0+0000",
            "datetime_string_field_2": datetime(
                year=2020, month=5, day=25, hour=17, minute=45, second=30, microsecond=0, tzinfo=timezone.utc,
            ),
            "number_string_field_1": "3.1428",
            "number_string_field_2": 3.1428,
            "integer_string_field_1": "9015",
            "integer_string_field_2": 9015,
            "float_string_field_1": "3.1428",
            "float_string_field_2": 3.1428,
        }
        val = FieldConversionValidator(data=data)
        val.run_validations()
        self.assertTrue(not has_errors(val.errors))
        validated_data = val.validated_data
        for key in validated_data:
            self.assertTrue(
                key in expected_validated_data,
                msg="Make sure that `expected_validated_data` has the expected keys",
            )
            validated_value = validated_data[key]
            expected_value = expected_validated_data[key]
            self.assertTrue(
                type(validated_value) is type(expected_value),
                msg=f"Validated value type: `{type(validated_value).__name__}` || Expected value type: `{type(expected_value).__name__}`",
            )
            self.assertTrue(
                validated_value == expected_value,
                msg=f"Validated value: `{validated_value}` || Expected value: `{expected_value}`",
            )

    def field_params_validator_helper(self, *, data: Dict[str, Any], should_be_valid: bool) -> None:
        val = FieldParamsValidator(data=data)
        self.assertTrue(val.five_letter_word.type_alias == "CustomStringField")
        self.assertTrue(val.five_letter_word.required is False)
        self.assertTrue(val.five_letter_word.nullable is True)
        val.run_validations()
        errors = val.errors
        num_errors = len(errors)
        if should_be_valid:
            self.assertTrue(num_errors == 0)
        else:
            self.assertTrue(num_errors > 0)
        if num_errors > 0:
            expected_error_description = (
                "The given custom string field is invalid. Must contain exactly 5 lower-case characters"
            )
            self.assertTrue(all([
                error.description == expected_error_description for error in errors
            ]))
        if num_errors == 0:
            self.assertTrue(
                len(val.validated_data) == 1,
            )
            target_value = val.get_validated_value("five_letter_word_target")
            if "five_letter_word_source" in data and data["five_letter_word_source"] is None:
                self.assertTrue(target_value is None)
            if "five_letter_word_source" in data and isinstance(data["five_letter_word_source"], str):
                self.assertTrue(target_value == data["five_letter_word_source"].upper())
            if "five_letter_word_source" not in data:
                self.assertTrue(target_value == "HELLO")

    def test_field_params_validator(self):
        self.field_params_validator_helper(data={"five_letter_word_source": "abcde"}, should_be_valid=True)
        self.field_params_validator_helper(data={}, should_be_valid=True)
        self.field_params_validator_helper(data={"five_letter_word_source": None}, should_be_valid=True)
        self.field_params_validator_helper(data={"five_letter_word_source": "abcdef"}, should_be_valid=False)
        self.field_params_validator_helper(data={"five_letter_word_source": "aBcDe"}, should_be_valid=False)

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

    def test_any_field_1(self):
        self.assert_validations(
            validator_model=AnyFieldValidator1,
            io=[
                {
                    "data": {"any_field_1": True},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": False},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": 1},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": 0},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": {}},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": []},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_1": None},
                    "should_be_valid": False,
                },
                {
                    "data": {},
                    "should_be_valid": False,
                },
            ],
        )

    def test_any_field_2(self):
        self.assert_validations(
            validator_model=AnyFieldValidator2,
            io=[
                {
                    "data": {},
                    "should_be_valid": True,
                },
                {
                    "data": {"any_field_2": None},
                    "should_be_valid": True,
                },
            ],
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
                    "data": {"json_string_field": '[1, 2, 3, null, "hello"]'},
                    "should_be_valid": True,
                },
                {
                    "data": {"json_string_field": None},
                    "should_be_valid": False,
                },
                {
                    "data": {"json_string_field": 'null'},
                    "should_be_valid": True,
                },
            ],
        )

    def test_email_id_field(self):
        self.assert_validations(
            validator_model=EmailIdStringFieldValidator,
            io=[
                {
                    "data": {"email_id_string_field": "hello@example.com"},
                    "should_be_valid": True,
                },
                {
                    "data": {"email_id_string_field": "hello@example.com."},
                    "should_be_valid": False,
                },
                {
                    "data": {"email_id_string_field": ""},
                    "should_be_valid": False,
                },
                {
                    "data": {"email_id_string_field": 123},
                    "should_be_valid": False,
                },
                {
                    "data": {"email_id_string_field": None},
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

    def test_uuid_field(self):
        self.assert_validations(
            validator_model=UuidFieldValidator,
            io=[
                {
                    "data": {"uuid_field": uuid.uuid4()},
                    "should_be_valid": True,
                },
                {
                    "data": {"uuid_field": str(uuid.uuid4())},
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

    def test_date_field(self):
        self.assert_validations(
            validator_model=DateValidator,
            io=[
                {
                    "data": {"date_field": utils.get_current_date()},
                    "should_be_valid": True,
                },
                {
                    "data": {"date_field": utils.get_current_date().strftime(DATE_FORMAT)},
                    "should_be_valid": False,
                },
                {
                    "data": {"date_field": utils.get_current_date().strftime("%Y-%m-%d")},
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

    def test_datetime_string_field_v2(self):
        dt_obj_1 = utils.get_current_datetime(timezone_aware=True)
        dt_obj_2 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC+05:30")
        dt_obj_3 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC+02:30")
        dt_obj_4 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC-03:30")
        self.assert_validations(
            validator_model=DatetimeStringValidatorV2,
            io=[
                {
                    "data": {"datetime_string_field_tz_aware_v2": dt_obj_1.strftime(DATETIME_FORMAT)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field_tz_aware_v2": dt_obj_2.strftime(DATETIME_FORMAT)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field_tz_aware_v2": dt_obj_3.strftime(DATETIME_FORMAT)},
                    "should_be_valid": False,  # timezone 'UTC+02:30' not allowed in validator
                },
                {
                    "data": {"datetime_string_field_tz_aware_v2": dt_obj_4.strftime(DATETIME_FORMAT)},
                    "should_be_valid": False,  # timezone 'UTC-03:30' not allowed in validator
                },
                {
                    "data": {"datetime_string_field_tz_naive_v2": dt_obj_1.replace(tzinfo=None).strftime(DATETIME_FORMAT_TZ_NAIVE)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field_tz_naive_v2": dt_obj_2.replace(tzinfo=None).strftime(DATETIME_FORMAT_TZ_NAIVE)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field_tz_naive_v2": dt_obj_3.replace(tzinfo=None).strftime(DATETIME_FORMAT_TZ_NAIVE)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_string_field_tz_naive_v2": dt_obj_4.replace(tzinfo=None).strftime(DATETIME_FORMAT_TZ_NAIVE)},
                    "should_be_valid": True,
                },
            ],
        )

    def test_datetime_field(self):
        self.assert_validations(
            validator_model=DatetimeValidator,
            io=[
                {
                    "data": {"datetime_field_tz_aware": utils.get_current_datetime(timezone_aware=True)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_aware": utils.get_current_datetime(timezone_aware=False)},
                    "should_be_valid": False,
                },
                {
                    "data": {"datetime_field_tz_aware": utils.get_current_datetime(timezone_aware=True).strftime(DATETIME_FORMAT)},
                    "should_be_valid": False,
                },
                {
                    "data": {"datetime_field_tz_naive": utils.get_current_datetime(timezone_aware=False)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_naive": utils.get_current_datetime(timezone_aware=True)},
                    "should_be_valid": False,
                },
                {
                    "data": {"datetime_field_tz_naive": utils.get_current_datetime(timezone_aware=False).strftime(DATETIME_FORMAT)},
                    "should_be_valid": False,
                },
            ],
        )

    def test_datetime_field_v2(self):
        dt_obj_1 = utils.get_current_datetime(timezone_aware=True)
        dt_obj_2 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC+05:30")
        dt_obj_3 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC+02:30")
        dt_obj_4 = utils.convert_datetime_timezone(dt_obj_1, tz_name="UTC-03:30")
        self.assert_validations(
            validator_model=DatetimeValidatorV2,
            io=[
                {
                    "data": {"datetime_field_tz_aware_v2": dt_obj_1},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_aware_v2": dt_obj_2},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_aware_v2": dt_obj_3},
                    "should_be_valid": False,  # timezone 'UTC+02:30' not allowed in validator
                },
                {
                    "data": {"datetime_field_tz_aware_v2": dt_obj_4},
                    "should_be_valid": False,  # timezone 'UTC-03:30' not allowed in validator
                },
                {
                    "data": {"datetime_field_tz_naive_v2": dt_obj_1.replace(tzinfo=None)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_naive_v2": dt_obj_2.replace(tzinfo=None)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_naive_v2": dt_obj_3.replace(tzinfo=None)},
                    "should_be_valid": True,
                },
                {
                    "data": {"datetime_field_tz_naive_v2": dt_obj_4.replace(tzinfo=None)},
                    "should_be_valid": True,
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
                {
                    "data": {"number_string_field": "-1.0"},
                    "should_be_valid": True,
                },
                {
                    "data": {"number_string_field": "-1.01"},
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
                {
                    "data": {"integer_string_field": "-1.0"},
                    "should_be_valid": False,
                },
            ],
        )

    def test_float_string_field(self):
        self.assert_validations(
            validator_model=FloatStringFieldValidator,
            io=[
                {
                    "data": {"float_string_field": "1.1"},
                    "should_be_valid": True,
                },
                {
                    "data": {"float_string_field": "1.0"},
                    "should_be_valid": True,
                },
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

