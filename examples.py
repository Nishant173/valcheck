from valcheck import base_validator, errors, fields, models


class UserDetailsValidator(base_validator.BaseValidator):
    name = fields.StringField(validators=[lambda name: len(name) > 0])
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
        error=models.Error(details="Monthly salary must be between $100,000 and $350,000 (and must be an even number)"),
    )
    other_info = fields.AnyField(required=False, nullable=True, default_func=lambda: None)

    # You can define model validator functions that receive the validated field data as an input.
    # Can be used to validate the entire model (after all individual fields are validated).
    def validate_birth_year_by_gender(validated_data):
        year, _, _ = validated_data['date_of_birth'].split('-')
        year = int(year)
        gender = validated_data['gender']
        if gender == 'Other' and year < 2000:
            return models.Error(details="Gender 'Other' is invalid for users born before the year 2000")
        return None


if __name__ == "__main__":
    validator = UserDetailsValidator(data={
        "name": "Sundar Pichai",
        "date_of_birth": "1970-11-25",
        "gender": "Male",
        "monthly_salary": 250_000,
        "other_info": {"fav_board_game": "chess", "fav_sport": "football"},
    })
    print("Validators:", *validator.list_validators(), sep="\n") # Lists all validators recognized

    try:
        validator.run_validations()
    except errors.ValidationError as err:
        print(f"Error info:\n{err.error_info}") # List having error info
    else:
        print(f"Validated data:\n{validator.validated_data}") # Dictionary having validated data (by field)