## Writing a simple validator (via the `ApiRequestValidator` class)

from pprint import pprint

from valcheck import fields
from valcheck.apis.validators import ApiRequestValidator
from valcheck.apis.exceptions import ApiException
from valcheck.apis import status_codes


DATE_FORMAT = "%Y-%m-%d"
GENDER_CHOICES = ("Female", "Male", "Other")


class PersonValidator(ApiRequestValidator):

    # To specify the HTTP status code of the error raised
    HTTP_STATUS_CODE: int = status_codes.HTTP_400_BAD_REQUEST

    name = fields.StringField(allow_empty=False)
    age = fields.IntegerField()
    gender = fields.ChoiceField(choices=GENDER_CHOICES)
    date_of_birth = fields.DateStringField(format_=DATE_FORMAT)


if __name__ == "__main__":
    data = {
        "name": "james murphy",
        "age": 30,
        "gender": "Male",
        "date_of_birth": "1980-05-25",
    }
    person_validator = PersonValidator(data=data)
    try:
        person_validator.run_validations(raise_exception=True)
    except ApiException as exc:
        pprint([error.as_dict() for error in exc.errors]) # Error list
        print(f"HTTP status code: {exc.http_status_code}")
    else:
        pprint(person_validator.validated_data) # Dictionary having validated data (by field)

