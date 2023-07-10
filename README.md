# valcheck
An open-source, lightweight, highly performant library for quick data validation

## Installation
```
pip install valcheck
```

## Usage
- Refer to the `examples/` folder, based on the **valcheck** version you are using

## Examples
```python

from pprint import pprint

from valcheck import fields, models, validator


def is_valid_name(s: str) -> bool:
    return len(s.strip().split(' ')) == 2


def clean_name(s: str) -> str:
    first, last = s.strip().split(' ')
    return f"{first.capitalize()} {last.capitalize()}"


class PersonValidator(validator.Validator):
    name = fields.StringField(
        allow_empty=False,
        required=True,
        nullable=False,
        converter_factory=clean_name,
        validators=[is_valid_name],
        error=models.Error(description="The name should include first and last name. Eg: `Sundar Pichai`"),
    )
    age = fields.IntegerField(
        validators=[lambda age: age >= 18],
        error=models.Error(description="The person must be an adult (at least 18 years old)"),
    )
    gender = fields.ChoiceField(
        choices=("Female", "Male"),
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "age": 30,
        "gender": "Male",
    }
    person_validator = PersonValidator(data=data)
    errors = person_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)
```