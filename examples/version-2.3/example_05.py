## Writing a validator having the `model_validator()` method

from datetime import datetime, date
from pprint import pprint
from typing import List

from valcheck import fields, models, validators

DATE_FORMAT = "%Y-%m-%d"


class PersonValidator(validators.Validator):
    name = fields.StringField(allow_empty=False)
    date_of_birth = fields.DateStringField(
        format_=DATE_FORMAT,
        converter_factory=lambda x: datetime.strptime(x, DATE_FORMAT).date(),
    )
    gender = fields.ChoiceField(choices=("Female", "Male"))

    def model_validator(self) -> List[models.Error]:
        """
        Used to validate the entire model, after all individual fields are validated.
        The output of this method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        errors = []
        name: str = self.get_validated_value("name")
        date_of_birth: date = self.get_validated_value("date_of_birth")
        gender: str = self.get_validated_value("gender")
        if name.replace(" ", "") == "":
            error = models.Error(
                description="Invalid - The given name only has whitespaces. Please pass in an actual name",
                initial_field_path="name",
            )
            errors.append(error)
        if gender == "Male" and date_of_birth.month == 12:
            error = models.Error(
                description="Invalid - We don't allow males born in the month of December",
                initial_field_path="date_of_birth/gender", # the error is in either `date_of_birth` or `gender`
            )
            errors.append(error)
        return errors


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "date_of_birth": "1980-05-25",
        "gender": "Male",
    }
    person_validator = PersonValidator(data=data)
    person_validator.run_validations()
    errors = person_validator.errors
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)
