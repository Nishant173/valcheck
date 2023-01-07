from pprint import pprint
from valcheck import base_validator, exceptions, fields, models


class PersonDetailsValidator(base_validator.BaseValidator):
    name = fields.StringField(allow_empty=False)
    age = fields.PositiveIntegerField()
    gender = fields.ChoiceField(choices=['Male', 'Female'])


if __name__ == "__main__":
    persons = [
        {
            "name": "Elon Musk",
            "age": -1,
            "gender": "Male-xxx",
        },
        {
            "name": "Sundar Pichai",
            "age": 45,
            "gender": "Male",
        },
        None,
        123,
    ]

    try:
        base_validator.validate_list_of_models_field(
            field='persons',
            field_value=persons,
            model=PersonDetailsValidator,
            error=models.Error(details={"message": "Invalid field 'persons'. Provide a valid list of person objects"})
        )
    except exceptions.ValidationException as exc:
        pprint(exc.error_info)