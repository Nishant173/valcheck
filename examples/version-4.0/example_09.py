## Writing your own custom re-usable fields

from datetime import datetime, timedelta, timezone
from pprint import pprint
from typing import List

from valcheck import fields, models, validators


DATETIME_UTC_FIELD = fields.AnyField(
    validators=[
        lambda x: isinstance(x, datetime) and x.tzinfo == timezone.utc,
    ],
    error=models.Error(description="Expected datetime object having timezone as UTC"),
    type_alias="DATETIME_UTC_FIELD",
)


class TimestampValidator(validators.Validator):
    start_timestamp = DATETIME_UTC_FIELD
    end_timestamp = DATETIME_UTC_FIELD

    def model_validator(self) -> List[models.Error]:
        errors = []
        if self.get_validated_value("start_timestamp") >= self.get_validated_value("end_timestamp"):
            error = models.Error(
                description="`start_timestamp` must be < `end_timestamp`",
                field_path_part="start_timestamp/end_timestamp",
            )
            errors.append(error)
        return errors


def main():
    dt_obj = datetime(
        year=2020,
        month=5,
        day=25,
        hour=10,
        minute=30,
        second=00,
    ).astimezone(timezone.utc)
    data = {
        "start_timestamp": dt_obj,
        "end_timestamp": dt_obj + timedelta(hours=10),
    }
    timestamp_validator = TimestampValidator(data=data)
    timestamp_validator.run_validations()
    errors = timestamp_validator.errors
    if errors:
        print("\nErrors")
        pprint([e.as_dict() for e in errors])
    else:
        print("\nValidated data")
        pprint(timestamp_validator.validated_data)


if __name__ == "__main__":
    main()

