## Writing a simple validator

from pprint import pprint

from valcheck import fields, validators

DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male", "Other")


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    age = fields.IntegerField()
    gender = fields.ChoiceField(choices=GENDER_CHOICES)
    date_of_birth = fields.DateStringField(format_=DATE_FORMAT)


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "age": 30,
        "gender": "Male",
        "date_of_birth": "1980-05-25",
    }
    person_validator = PersonValidator(data=data)
    errors = person_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

