from valcheck import base_validator, errors, fields


class UserValidator(base_validator.BaseValidator):
    id = fields.UuidStringField()
    first_name = fields.StringField()
    middle_name = fields.StringField(required=False, nullable=True, default_func=lambda: None)
    last_name = fields.StringField()
    date_of_birth = fields.DateStringField(format_="%Y-%m-%d")
    monthly_salary = fields.PositiveIntegerField(
        required=False,
        nullable=True,
        default_func=lambda: None,
        validators=[lambda salary: 100_000 <= salary <= 350_000],
        error_kwargs={
            "details": "Annual salary must be between 100,000 and 350,000 (USD)",
            "source": "",
            "code": "",
        },
    )
    hobbies = fields.MultiChoiceField(
        choices=['football', 'hockey', 'cricket', 'rugby', 'kick-boxing'],
    )
    extra_info = fields.DictionaryField(
        validators=[lambda dict_obj: "fav_sport" in dict_obj],
        error_kwargs={
            "details": "Expected following params in extra_info field: fav_sport",
            "source": "",
            "code": "",
        },
    )

    # Model validator functions - Can be used to validate the entire model.
    # If there is an error, return dictionary having error kwargs, otherwise return None
    def validate_fav_sport(values):
        if values['extra_info']['fav_sport'] not in values['hobbies']:
            return {
                "details": "Invalid entry. Your favourite sport is not one of your hobbies",
                "source": "",
                "code": "",
            }
        return None


def without_exception(*, validator: base_validator.BaseValidator) -> None:
    if validator.is_valid():
        print(f"Validated data: {validator.validated_data}")
    else:
        print(f"Errors: {validator.errors}")


def with_exception(*, validator: base_validator.BaseValidator) -> None:
    try:
        validator.is_valid(raise_exception=True, many=True)
    except errors.ValidationError as err:
        print("ValidationError was raised!")
        print(f"Errors: {err.error_info}")
    else:
        print(f"Validated data: {validator.validated_data}")


if __name__ == "__main__":
    validator = UserValidator(data={
        "id": "d82283aa-2eae-4f96-abc7-0ec69a557a84",
        "first_name": "Sundar",
        "last_name": "Pichai",
        "date_of_birth": "1970-11-25",
        "monthly_salary": 250_000,
        "hobbies": ['football', 'hockey', 'cricket'],
        "extra_info": {"fav_board_game": "chess", "fav_sport": "football"},
    })
    print("Validators:", *validator.list_validators(), sep="\n") # Lists all validators recognized

    # without_exception(validator=validator)
    with_exception(validator=validator)