# valcheck
Lightweight package for quick data validation

## Installation
- You can install this library with `pip install valcheck` or `pip install valcheck==<version>`

## Usage
```python
from valcheck import base_validator, fields


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


validator = UserValidator({
    "id": "d82283aa-2eae-4f96-abc7-0ec69a557a84",
    "email": "first_name123@yahoo.co.in",
    "date_of_birth": "1980-07-31",
    "age": 26,
    "age_category": "18-30",
    "hobbies": ['cricket', 'hockey'],
    "extra_info": {"fav_board_game": "chess", "fav_sport": "football"},
    "date_of_registration": None,
})
if validator.is_valid(raise_exception=False):
    print(validator.validated_data)
else:
    print(validator.errors)
```
