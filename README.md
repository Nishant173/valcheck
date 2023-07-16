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

## Performance benchmarks
- On comparison of the performance of Django Rest Framework's (version 3.14.0) serializer with Valcheck's
validator, we found that Valcheck (version 0.6.0) is ~3.8 times faster for cases where the data is
valid, and ~2.7 times faster for cases where the data is invalid.
- These numbers are averaged over 25,000 iterations.

```python
from rest_framework import serializers
from valcheck import fields, models, validator

DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male")


class PersonDrf(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    dob = serializers.DateField(format=DATE_FORMAT)


class PersonValcheck(validator.Validator):
    name = fields.StringField()
    age = fields.IntegerField()
    gender = fields.ChoiceField(choices=GENDER_CHOICES)
    dob = fields.DateStringField(format_=DATE_FORMAT)
```
