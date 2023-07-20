## Writing a validator with various options for each field
## Refer to docstring of `valcheck.fields.Field`

from datetime import datetime
from pprint import pprint

from valcheck import fields, models, validator

DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male", "N/A")


class PersonValidator(validator.Validator):
    name = fields.StringField(allow_empty=False)
    age = fields.IntegerField()
    gender = fields.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        default_factory=lambda: "N/A",
    )
    date_of_birth = fields.DateStringField(
        format_=DATE_FORMAT,
        source="Date of birth",
        target="Date of birth",
        required=True,
        nullable=False,
        converter_factory=lambda x: datetime.strptime(x, DATE_FORMAT).date(),
        validators=[
            lambda x: datetime.strptime(x, DATE_FORMAT).date().month <= 6,
        ],
        error=models.Error(description="Invalid date of birth. Person born in second half of the year is not allowed"),
    )


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "age": 30,
        "gender": "Male",
        "Date of birth": "1980-05-25",
    }
    person_validator = PersonValidator(data=data)
    errors = person_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

