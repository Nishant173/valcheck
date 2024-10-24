## Writing validators with inheritance - you can over-write fields from parent classes

from pprint import pprint
from typing import Type

from valcheck import fields, models, validators


class BaseUserValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    age = fields.IntegerField(
        validators=[lambda x: x >= 18],
        error=models.Error(description="User must be atleast 18 years old"),
    )
    gender = fields.ChoiceField(choices=("Female", "Male"))


class AdminUserValidator(BaseUserValidator):
    gender = fields.ChoiceField(
        choices=("Female", "Male"),
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )


class RegularUserValidator(BaseUserValidator):
    pass


def main():
    data = {
        "name": "james murphy",
        "age": 30,
        "gender": "Male",
    }
    validator_class: Type[BaseUserValidator] = AdminUserValidator
    # validator_class: Type[BaseUserValidator] = RegularUserValidator
    user_validator = validator_class(data=data)
    print("\nField validators")
    pprint(user_validator.list_field_validators())
    user_validator.run_validations()
    errors = user_validator.errors
    if errors:
        print("\nErrors")
        pprint([e.as_dict() for e in errors])
    else:
        print("\nValidated data")
        pprint(user_validator.validated_data)


if __name__ == "__main__":
    main()

