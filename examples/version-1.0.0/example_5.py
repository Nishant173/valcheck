## Writing a validator having the `model_validator()` method

from datetime import datetime, date
from pprint import pprint
from typing import List

from valcheck import fields, models, validator

DATE_FORMAT = "%Y-%m-%d"


class PersonValidator(validator.Validator):
    name = fields.StringField(allow_empty=False)
    date_of_birth = fields.DateStringField(
        format_=DATE_FORMAT,
        converter_factory=lambda x: datetime.strptime(x, DATE_FORMAT).date(),
    )
    gender = fields.ChoiceField(choices=("Female", "Male"))

    def model_validator(self) -> List[models.Error]:
        """
        Used to validate the entire model, after all individual fields are validated.
        The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        errors = []
        date_of_birth: date = self.get_validated_value("date_of_birth")
        gender: str = self.get_validated_value("gender")
        if gender == "Male" and date_of_birth.month == 12:
            errors.append(
                models.Error(description="Invalid - We don't allow males born in the month of December")
            )
        return errors


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "date_of_birth": "1980-05-25",
        "gender": "Male",
    }
    person_validator = PersonValidator(data=data)
    errors = person_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)
