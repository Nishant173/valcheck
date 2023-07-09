from pprint import pprint

from valcheck import exceptions, fields, models, validator


class PersonValidator(validator.Validator):
    name = fields.StringField(allow_empty=False)
    age = fields.IntegerField(
        validators=[lambda age: age >= 18],
        error=models.Error(description="The person must be an adult (at least 18 y/o)"),
    )
    gender = fields.ChoiceField(
        choices=("Female", "Male"),
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )
    annual_salary_in_inr = fields.IntegerField(
        converter_factory=float,
        validators=[lambda s: s >= 0],
        error=models.Error(description="The annual salary (in INR) must be a positive integer"),
    )


if __name__ == "__main__":
    person_validator = PersonValidator(data={
        "name": "James Murphy",
        "age": 30,
        "gender": "Male",
        "annual_salary_in_inr": 4_50_000,
    })
    print("\nField validators")
    pprint(person_validator.list_field_validators())

    try:
        person_validator.run_validations(raise_exception=True)
    except exceptions.ValidationException as exc:
        print("\nError info")
        pprint(exc.as_dict())
    else:
        print("\nValidated data")
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)
