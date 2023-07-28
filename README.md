# valcheck
An open-source, lightweight, highly performant library for quick data validation

## Installation
```
pip install valcheck
```

## Usage
- Refer to the `examples/` folder, based on the **valcheck** version you are using

## Performance benchmarks
- On comparison of the performance of Django Rest Framework's (version 3.14.0) serializer with Valcheck's
validator, we found that Valcheck (version 1.2) is ~3.8 times faster for cases where the data is
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
