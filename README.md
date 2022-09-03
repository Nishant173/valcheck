# valcheck
Lightweight package for quick data validation

## Installation
- You can install this library with `pip install valcheck` or `pip install valcheck==<version>`

## Usage
```python
from valcheck import base_validator, fields


def validate_fav_sport(values):
    if values['extra_info']['fav_sport'] not in values['hobbies']:
        return {"details": "Invalid entry. Your favourite sport is not one of your hobbies"}
    return None


def validate_birth_month(values):
    if 'date_of_birth' in values:
        dob = values['date_of_birth']
        if dob is None:
            return None
        year, month, day = dob.split('-')
        if int(month) == 12:
            return {"details": "Invalid entry. Cannot register a user born in December"}
    return None


class UserValidator(base_validator.BaseValidator):
    id = fields.UuidStringField()
    first_name = fields.StringField()
    middle_name = fields.StringField(required=False, nullable=True)
    last_name = fields.StringField()
    date_of_birth = fields.DateStringField(format_="%Y-%m-%d")
    annual_salary = fields.PositiveIntegerField(
        required=False,
        nullable=False,
        validators=[lambda salary: 100_000 <= salary <= 350_000],
        error_kwargs={
            "details": "Annual salary must be between 100,000 and 350,000 (USD)",
            "source": "",
            "code": "",
        },
    )
    hobbies = fields.MultiChoiceField(
        choices=['football', 'hockey', 'cricket', 'rugby', 'kick-boxing'],
    )
    extra_info = fields.DictionaryField(
        validators=[lambda dict_obj: "fav_sport" in dict_obj],
        error_kwargs={
            "details": "Expected following params in extra_info field: fav_sport",
            "source": "",
            "code": "",
        },
    )

    class Meta:
        # If there is an error, returns dictionary having error kwargs, else returns None
        class_validators = [validate_birth_month, validate_fav_sport]


if __name__ == "__main__":
    validator = UserValidator(data={
        "id": "d82283aa-2eae-4f96-abc7-0ec69a557a84",
        "first_name": "Sundar",
        "middle_name": None,
        "last_name": "Pichai",
        "date_of_birth": "1980-11-25",
        "annual_salary": 250_000,
        "hobbies": ['football', 'hockey', 'cricket'],
        "extra_info": {"fav_board_game": "chess", "fav_sport": "football"},
    })
    if validator.is_valid(raise_exception=False):
        print(f"Validated data: {validator.validated_data}")
    else:
        print(f"Errors: {validator.errors}")
```