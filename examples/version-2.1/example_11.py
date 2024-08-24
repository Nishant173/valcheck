## Using Validator.get_representation()

import json
from pprint import pprint

from valcheck import fields, validators


GENDERS = (
    "Male",
    "Female",
    "Other",
)

COLORS = (
    "red",
    "blue",
    "yellow",
    "orange",
    "green",
    "white",
    "black",
    "pink",
)


class HobbyValidator(validators.Validator):
    id = fields.UuidStringField()
    name = fields.StringField(allow_empty=False, source="hobby_name")


class PersonalInfoValidator(validators.Validator):
    full_name = fields.StringField(allow_empty=False)
    favourite_hobby = fields.ModelDictionaryField(validator_model=HobbyValidator)
    other_hobbies = fields.ModelListField(validator_model=HobbyValidator, allow_empty=False)
    extra_info = fields.JsonStringField(required=False, nullable=True, default_factory=lambda: None, converter_factory=lambda x: json.loads(x))
    gpa = fields.FloatStringField(required=False, nullable=True, default_factory=lambda: None)
    date_of_birth = fields.DateStringField(format_="%d %B, %Y", required=False, nullable=True, default_factory=lambda: None)
    datetime_of_birth = fields.DatetimeStringField(format_="%Y-%m-%d %H:%M:%S %z", required=False, nullable=True, default_factory=lambda: None)
    is_disabled = fields.BooleanField(required=False, nullable=True, default_factory=lambda: None)
    gender = fields.ChoiceField(choices=GENDERS, required=False, nullable=True, default_factory=lambda: None)
    favourite_colors = fields.MultiChoiceField(choices=COLORS, required=False, nullable=True, default_factory=lambda: None)


if __name__ == "__main__":
    data = {
        "full_name": "James Murphy",
        "favourite_hobby": {
            "id": "7e41ffc5-1106-4ad0-8aee-4a56c8d39ed6",
            "hobby_name": "coding",
        },
        "other_hobbies": [
            {
                "id": "9876dda8-c58d-43fd-8358-8c21a9a26613",
                "hobby_name": "hobby #1",
            },
            {
                "id": "9876dda8-c58d-43fd-8358-8c21a9a26614",
                "hobby_name": "hobby #2",
            },
            {
                "id": "9876dda8-c58d-43fd-8358-8c21a9a26615",
                "hobby_name": "hobby #3",
            },
        ],
        "extra_info": '{"key1": "value1", "key2": "value2"}',
        "gpa": "3.1",
        "date_of_birth": "18 August, 2002",
        "datetime_of_birth": "2002-08-18 07:54:55 +0000",
        "is_disabled": False,
        "gender": "Male",
        "favourite_colors": ["red", "orange"],
    }
    personal_info_validator = PersonalInfoValidator(data=data)
    representation = personal_info_validator.get_representation(key="source")
    print("Representation")
    pprint(representation)
    print("\n\n")
    errors = personal_info_validator.run_validations()
    if errors:
        print("Errors")
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        print("Validated data")
        pprint(personal_info_validator.validated_data) # Dictionary having validated data (by field)

