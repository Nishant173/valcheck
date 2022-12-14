from pprint import pprint
from valcheck import base_validator, exceptions, fields, models


class UserDetailsValidator(base_validator.BaseValidator):
    name = fields.StringField(empty_string_allowed=False)
    date_of_birth = fields.DateStringField(format_="%Y-%m-%d")
    gender = fields.ChoiceField(choices=('Male', 'Female', 'Other'))
    monthly_salary = fields.PositiveIntegerField(
        required=False,
        nullable=True,
        default_func=lambda: None,
        validators=[
            lambda salary: 100_000 <= salary <= 350_000,
            lambda salary: salary % 2 == 0,
        ],
        error=models.Error(details={"message": "Monthly salary must be between $100,000 and $350,000 (and must be an even number)"}),
    )
    some_bytes_object = fields.BytesField()
    other_info = fields.AnyField(required=False, nullable=True, default_func=lambda: None)

    # You can define the model validator method that receives the validated field data as an input.
    # Can be used to validate the entire model (after all individual fields are validated).
    def model_validator(self, *, validated_data):
        year, _, _ = validated_data['date_of_birth'].split('-')
        year = int(year)
        gender = validated_data['gender']
        if gender == 'Other' and year < 2000:
            return models.Error(details={"message": "Gender 'Other' is invalid for users born before the year 2000"})
        return None


if __name__ == "__main__":
    validator = UserDetailsValidator(data={
        "name": "Sundar Pichai",
        "date_of_birth": "1970-11-25",
        "gender": "Male",
        "monthly_salary": 250_000,
        "some_bytes_object": b'xaxaxaxa',
        "other_info": {"fav_board_game": "chess", "fav_sport": "football"},
    })
    print("\nField validators")
    pprint(validator.list_field_validators())

    try:
        validator.run_validations()
    except exceptions.ValidationException as exc:
        print("\nError info")
        pprint(exc.error_info) # List having error info
    else:
        print("\nValidated data")
        pprint(validator.validated_data) # Dictionary having validated data (by field)