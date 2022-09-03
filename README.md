# valcheck
Lightweight package for quick data validation

## Installation
- You can install this library with `pip install valcheck` or `pip install valcheck==<version>`

## Usage
```python
from valcheck import base_validator, fields


def validate_fav_sport(values):
    """If there is an error, returns dictionary having error kwargs, else returns None"""
    if values['extra_info']['fav_sport'] not in values['hobbies']:
        return {"details": "Invalid entry. Your favourite sport is not one of your hobbies"}
    return None


def validate_reg_date(values):
    """If there is an error, returns dictionary having error kwargs, else returns None"""
    if 'date_of_registration' in values:
        if values['date_of_registration'] is None:
            return None
        year, month, day = values['date_of_registration'].split('-')
        if int(month) in [10, 11, 12]:
            return {"details": "Invalid entry. Cannot have date of registration in Q4 of the calendar year"}
    return None


class UserValidator(base_validator.BaseValidator):
    id = fields.UuidStringField()
    email = fields.EmailIdField()
    date_of_birth = fields.DateStringField()
    age = fields.PositiveIntegerField(
        validators=[
            lambda age: 18 <= age <= 100,
            lambda age: age % 2 == 0,
        ],
        error_kwargs={
            "source": "",
            "code": "",
            "details": "provide age between 18-100 (must also be an even number)",
        },
    )
    age_category = fields.ChoiceField(
        choices=['under-18', '18-30', '31-60', '60+'],
    )
    hobbies = fields.MultiChoiceField(
        choices=['football', 'hockey', 'cricket', 'rugby', 'kick-boxing'],
    )
    extra_info = fields.DictionaryField(
        required=True,
        nullable=False,
        validators=[
            lambda dict_obj: "fav_board_game" in dict_obj,
            lambda dict_obj: "fav_sport" in dict_obj,
        ],
        error_kwargs={
            "details": "expected following params in `extra_info` field: ['fav_board_game', 'fav_sport']",
        },
    )
    date_of_registration = fields.DateStringField(
        format_="%Y-%m-%d",
        required=False,
        nullable=True,
    )

    class Meta:
        class_validators = [
            validate_fav_sport,
            validate_reg_date,
        ]


if __name__ == "__main__":
    validator = UserValidator(data={
        "id": "d82283aa-2eae-4f96-abc7-0ec69a557a84",
        "email": "first_name123@yahoo.co.in",
        "date_of_birth": "1980-07-31",
        "age": 26,
        "age_category": "18-30",
        "hobbies": ['cricket', 'hockey', 'football'],
        "extra_info": {"fav_board_game": "chess", "fav_sport": "football"},
        "date_of_registration": "2020-01-25",
    })
    if validator.is_valid(raise_exception=False):
        print(validator.validated_data)
    else:
        print(validator.errors)
```