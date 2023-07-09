from datetime import datetime, date
from pprint import pprint
from typing import List

from valcheck import exceptions, fields, models, validator


OCCUPATION_TYPE_CHOICES = (
    "Entrepreneur",
    "Government employee",
    "Retired",
    "Salaried employee (Private company)",
    "Student",
    "Unemployed",
)
ANNUAL_SALARY_RANGE_IN_INR = (
    "0 to 5,00,000 INR",
    "5,00,000+ to 10,00,000 INR",
    "10,00,000+ to 18,00,000 INR",
    "18,00,000+ to 25,00,000 INR",
    "25,00,000+ to 40,00,000 INR",
    "40,00,000+ to 60,00,000 INR",
    "60,00,000+ INR",
)


class UserJobHistoryItemValidator(validator.Validator):
    company = fields.StringField(allow_empty=False)
    start_date = fields.DateStringField(
        converter_factory=lambda date_string: datetime.strptime(date_string, "%Y-%m-%d").date(),
    )
    end_date = fields.DateStringField(
        converter_factory=lambda date_string: datetime.strptime(date_string, "%Y-%m-%d").date(),
    )
    is_current_company = fields.BooleanField()
    designation = fields.StringField(allow_empty=False)
    annual_salary = fields.ChoiceField(
        choices=ANNUAL_SALARY_RANGE_IN_INR,
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )
    reason_for_leaving = fields.StringField(
        allow_empty=False,
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )

    def model_validator(self) -> List[models.Error]:
        errors = []
        company = self.get_field_value("company")
        reason_for_leaving = self.get_field_value("reason_for_leaving")
        start_date: date = self.get_field_value("start_date")
        end_date: date = self.get_field_value("end_date")
        if start_date > end_date:
            msg = f"For '{company}' company, start date must be less than or equal to end date"
            errors.append(models.Error(description=msg))
        if (end_date - start_date).days < 365 and reason_for_leaving is None:
            msg = (
                f"For '{company}' company, since you worked here for less than 365 days, please provide"
                " your reason for leaving the company"
            )
            errors.append(models.Error(description=msg))
        return errors


class UserAddressValidator(validator.Validator):
    country = fields.StringField(allow_empty=False)
    state = fields.StringField(allow_empty=False)
    city = fields.StringField(allow_empty=False)
    street = fields.StringField(allow_empty=False)
    postal_code = fields.StringField(
        allow_empty=False,
        validators=[
            lambda code: len(code) == 6,
            lambda code: all([c.isdigit() for c in code]),
        ],
        error=models.Error(description="Postal code needs to be a 6 digit numerical code"),
    )
    is_mailing_address = fields.BooleanField(
        required=False,
        default_factory=lambda: False,
        converter_factory=lambda x: str(x).upper(),
    )


class UserBasicDetailsValidator(validator.Validator):
    name = fields.StringField(allow_empty=False)
    dob = fields.DateStringField(
        converter_factory=lambda date_string: datetime.strptime(date_string, "%Y-%m-%d").date(),
    )
    occupation_type = fields.ChoiceField(choices=OCCUPATION_TYPE_CHOICES)
    annual_salary = fields.ChoiceField(choices=ANNUAL_SALARY_RANGE_IN_INR)
    primary_address = fields.ModelDictionaryField(validator_model=UserAddressValidator)
    secondary_address = fields.ModelDictionaryField(
        validator_model=UserAddressValidator,
        required=False,
        nullable=True,
        default_factory=lambda: None,
    )
    job_history = fields.ModelListField(
        validator_model=UserJobHistoryItemValidator,
        required=False,
        default_factory=lambda: [],
    )


if __name__ == "__main__":
    user_basic_details_validator = UserBasicDetailsValidator(data={
        "name": "James Murphy",
        "dob": "1983-02-18",
        "occupation_type": "Salaried employee (Private company)",
        "annual_salary": "0 to 5,00,000 INR",
        "primary_address": {
            "country": "India",
            "state": "Maharashtra",
            "city": "Mumbai",
            "street": "XYZ #101",
            "postal_code": "400999",
            "is_mailing_address": True,
        },
        "secondary_address": None,
        "job_history": [
            {
                "company": "Amazon",
                "start_date": "2010-01-01",
                "end_date": "2010-06-30",
                "is_current_company": False,
                "designation": "SDE 1",
                "annual_salary": None,
                "reason_for_leaving": "Some reason #1",
            },
            {
                "company": "Google",
                "start_date": "2010-07-15",
                "end_date": "2011-12-31",
                "is_current_company": True,
                "designation": "SDE 2",
                "annual_salary": None,
                "reason_for_leaving": "Some reason #2",
            },
        ],
    })
    print("\nField validators")
    pprint(user_basic_details_validator.list_field_validators())

    try:
        user_basic_details_validator.run_validations(raise_exception=True)
    except exceptions.ValidationException as exc:
        print("\nError info")
        pprint(exc.as_dict())
    else:
        print("\nValidated data")
        pprint(user_basic_details_validator.validated_data) # Dictionary having validated data (by field)
