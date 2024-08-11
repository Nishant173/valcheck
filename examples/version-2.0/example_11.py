## Using Validator.get_representation()

from pprint import pprint

from valcheck import fields, validators


class HobbyValidator(validators.Validator):
    hobby_id = fields.IntegerField()
    hobby_name = fields.StringField(allow_empty=False, source="hobby_name_source", target="hobby_name_target")


class PersonValidator(validators.Validator):
    person_name = fields.StringField(allow_empty=False, source="person_name_source", target="person_name_target")
    hobby = fields.ModelDictionaryField(validator_model=HobbyValidator)
    hobbies = fields.ModelListField(validator_model=HobbyValidator, allow_empty=False)


if __name__ == "__main__":
    data = {
        "person_name_source": "james murphy",
        "hobby": {
            "hobby_id": 1,
            "hobby_name_source": "Hobby #1",
        },
        "hobbies": [
            {
                "hobby_id": 1,
                "hobby_name_source": "Hobby #1",
            },
            {
                "hobby_id": 2,
                "hobby_name_source": "Hobby #2",
            },
            {
                "hobby_id": 3,
                "hobby_name_source": "Hobby #3",
            },
        ],
    }
    person_validator = PersonValidator(data=data)
    representation = person_validator.get_representation(key="field_identifier")
    print("Representation")
    pprint(representation)
    print("\n\n")
    errors = person_validator.run_validations()
    if errors:
        print("Errors")
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        print("Validated data")
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

