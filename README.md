# valcheck
An open-source, lightweight, highly performant, and **predictable** library for quick data validation.

## Installation
```
pip install valcheck
```

## Usage
- Refer to the `examples/` folder, based on the **valcheck** version you are using.

```python
from valcheck import fields, models, validators

DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male")


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    date_of_birth = fields.DateStringField(format_=DATE_FORMAT)
    gender = fields.ChoiceField(choices=GENDER_CHOICES)
    num_friends = fields.IntegerField()
```
