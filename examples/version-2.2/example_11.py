## Using Validator.get_representation()

import json
from pprint import pprint

from valcheck import fields, validators


NOT_REQUIRED_AND_NULLABLE = dict(
    required=False,
    nullable=True,
    default_factory=lambda: None,
)

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
    id = fields.UuidStringField(
        source="hobby_id",
        target="hobby_id_target",
        converter_factory=lambda x: f"<ID: {x}>",
    )
    name = fields.StringField(allow_empty=False)


class PersonalInfoValidator(validators.Validator):
    full_name = fields.StringField(allow_empty=False)
    favourite_hobby = fields.ModelDictionaryField(validator_model=HobbyValidator)
    other_hobbies = fields.ModelListField(validator_model=HobbyValidator, allow_empty=False)
    extra_info = fields.JsonStringField(converter_factory=json.loads, **NOT_REQUIRED_AND_NULLABLE)
    gpa = fields.FloatStringField(**NOT_REQUIRED_AND_NULLABLE)
    date_of_birth = fields.DateStringField(format_="%d %B, %Y", **NOT_REQUIRED_AND_NULLABLE)
    datetime_of_birth = fields.DatetimeStringField(format_="%Y-%m-%d %H:%M:%S %z", **NOT_REQUIRED_AND_NULLABLE)
    is_disabled = fields.BooleanField(**NOT_REQUIRED_AND_NULLABLE)
    gender = fields.ChoiceField(choices=GENDERS, **NOT_REQUIRED_AND_NULLABLE)
    favourite_colors = fields.MultiChoiceField(choices=COLORS, **NOT_REQUIRED_AND_NULLABLE)


if __name__ == "__main__":
    # List the registered field validators
    print("-" * 100, "\n", sep="")
    field_validators = PersonalInfoValidator(data={}).list_field_validators()
    print("Field Validators")
    pprint(field_validators)

    # View the representation for the Validator
    print("-" * 100, "\n", sep="")
    representation = PersonalInfoValidator(data={}).get_representation(key="source")
    print("Representation")
    pprint(representation)

    # Validate the data
    print("-" * 100, "\n", sep="")
    data = {
        "full_name": "James Murphy",
        "favourite_hobby": {
            "hobby_id": "7e41ffc5-1106-4ad0-8aee-4a56c8d39ed6",
            "name": "coding",
        },
        "other_hobbies": [
            {
                "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26613",
                "name": "hobby #1",
            },
            {
                "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26614",
                "name": "hobby #2",
            },
            {
                "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26615",
                "name": "hobby #3",
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
    errors = personal_info_validator.run_validations()
    if errors:
        print("Errors")
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        print("Validated data")
        pprint(personal_info_validator.validated_data) # Dictionary having validated data (by field)

