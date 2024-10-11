## Writing a simple validator

from pprint import pprint

from valcheck import fields, validators

DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male", "Other")


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    date_of_birth = fields.DateStringField(format_=DATE_FORMAT)
    gender = fields.ChoiceField(choices=GENDER_CHOICES)
    num_friends = fields.IntegerField()


def main():
    data = {
        "name": "james murphy",
        "date_of_birth": "1980-05-25",
        "gender": "Male",
        "num_friends": 10,
    }
    person_validator = PersonValidator(data=data)
    person_validator.run_validations()
    errors = person_validator.errors
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)


if __name__ == "__main__":
    main()
