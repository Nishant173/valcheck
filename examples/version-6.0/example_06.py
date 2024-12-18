## Writing a validator having the `context` property

from pprint import pprint
from typing import List

from valcheck import fields, models, validators


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    gender = fields.ChoiceField(choices=("Female", "Male", "N/A"))

    def model_validator(self) -> List[models.Error]:
        """
        Used to validate the entire model, after all individual fields are validated.
        The output of this method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        errors = []
        user_id = self.context.get("user_id")
        if user_id and isinstance(user_id, int):
            user_id_is_odd: bool = user_id % 2 != 0
            gender: str = self.get_validated_value("gender")
            if user_id_is_odd and gender not in ("Female", "Male"):
                error = models.Error(
                    description="Invalid gender - Please use one of ('Female', 'Male') for an odd user ID",
                    field_path_part="gender",
                )
                errors.append(error)
        return errors


def main():
    data = {
        "name": "james murphy",
        "gender": "N/A",
    }
    ## Any context can be passed into the validator to aid validations
    context = {
        "user_id": 2,
    }
    person_validator = PersonValidator(data=data, context=context)
    person_validator.run_validations()
    errors = person_validator.errors
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)


if __name__ == "__main__":
    main()

