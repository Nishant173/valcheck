"""
This is a snippet that compares valcheck (version 1.5.x) validators with Django (4.2.3) / DjangoRestFramework (3.14.0) serializers
"""

import functools
import time

from rest_framework import serializers
from valcheck import fields, models, validator

DATE_FORMAT = "%Y-%m-%d"
NUM_REPITITIONS = 25_000


def repeat(num_times):
    """Decorator that executes the decorated function `num_times` times"""
    def repeat_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return repeat_decorator


def timer(func):
    """Decorator that prints the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        time_taken_in_secs = round(end - start, 3)
        print(f"Executed {func._name_!r} in: {time_taken_in_secs} secs")
        return result
    return wrapper_timer


class PersonDrf(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=("Female", "Male"))
    dob = serializers.DateField(format=DATE_FORMAT)


class PersonValcheck(validator.Validator):
    name = fields.StringField(
        allow_empty=False,
        error=models.Error(description="The name should include first and last name. Eg: `Sundar Pichai`"),
    )
    age = fields.IntegerField(
        validators=[lambda age: age >= 18],
        error=models.Error(description="The person must be an adult (at least 18 years old)"),
    )
    gender = fields.ChoiceField(choices=("Female", "Male"))
    dob = fields.DateStringField(format_=DATE_FORMAT)


@timer
@repeat(num_times=NUM_REPITITIONS)
def drf_serializer(data: dict):
    ser = PersonDrf(data=data)
    is_valid = ser.is_valid()
    if is_valid:
        return ser.validated_data
    return ser.errors


@timer
@repeat(num_times=NUM_REPITITIONS)
def valcheck_validator(data: dict):
    val = PersonValcheck(data=data)
    errors = val.run_validations()
    if errors:
        return [error.as_dict() for error in errors]
    return val.validated_data


if __name__ == "__main__":
    valid_data = {"name": "james murphy", "age": 30, "gender": "Male", "dob": "2000-01-16"}
    d1 = drf_serializer(valid_data)
    v1 = valcheck_validator(valid_data)

    invalid_data = {"name": 123, "age": "hello", "gender": "haha", "dob": "2000-01-16 --"}
    d2 = drf_serializer(invalid_data)
    v2 = valcheck_validator(invalid_data)
