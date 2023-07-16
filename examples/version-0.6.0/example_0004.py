from pprint import pprint
from typing import List

from valcheck import fields, models, validator


class PersonValidator(validator.Validator):
    name = fields.StringField(allow_empty=False)
    gender = fields.ChoiceField(choices=("Female", "Male", "Other"))

    def model_validator(self) -> List[models.Error]:
        errors = []
        user_id = self.context.get("user_id")
        if user_id and isinstance(user_id, int):
            user_id_is_odd = user_id % 2 != 0
            gender = self.get_field_value("gender")
            if (
                user_id_is_odd
                and gender not in ("Female", "Male")
            ):
                errors.append(models.Error(description="Invalid `gender` for an odd user ID"))
        return errors


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "gender": "Other",
    }
    context = {
        "user_id": 2,
    }
    person_validator = PersonValidator(data=data, context=context)
    errors = person_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

