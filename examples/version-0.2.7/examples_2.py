from pprint import pprint
from valcheck import base_validator, exceptions, fields, models


class PersonDetailsValidator(base_validator.BaseValidator):
    name = fields.StringField(
        allow_empty=False,
        error=models.Error(details={"message": "Name must be a non-empty string"}),
    )
    age = fields.PositiveIntegerField(
        validators=[lambda age: age % 2 == 0],
        error=models.Error(details={"message": "Age must be an even number"}),
    )
    gender = fields.ChoiceField(
        choices=['Male', 'Female'],
        error=models.Error(details={"message": "Gender must be one of ['Male', 'Female']"}),
    )


if __name__ == "__main__":
    persons = [
        {
            "name": "Elon Musk",
            "age": 53,
            "gender": "Male-xxx",
        },
        {
            "name": "Sundar Pichai",
            "age": 46,
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
        )
    except exceptions.ValidationException as exc:
        pprint(exc.error_info)