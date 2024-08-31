## Writing a validator with an advanced field i.e; `valcheck.fields.ModelDictionaryField`

from pprint import pprint

from valcheck import fields, models, validators


class AddressValidator(validators.Validator):
    country = fields.StringField(allow_empty=False)
    state = fields.StringField(allow_empty=False)
    city = fields.StringField(allow_empty=False)
    street = fields.StringField(allow_empty=False)
    postal_code = fields.StringField(
        allow_empty=False,
        validators=[
            lambda code: len(code) == 6,
            lambda code: all([c.isdigit() for c in code]),
        ],
        error=models.Error(description="Postal code needs to be a 6 digit numerical code"),
    )
    is_mailing_address = fields.BooleanField()


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    address = fields.ModelDictionaryField(validator_model=AddressValidator)


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "address": {
            "country": "India",
            "state": "Maharashtra",
            "city": "Mumbai",
            "street": "XYZ #101",
            "postal_code": "400999",
            "is_mailing_address": True,
        },
    }
    person_validator = PersonValidator(data=data)
    person_validator.run_validations()
    errors = person_validator.errors
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

