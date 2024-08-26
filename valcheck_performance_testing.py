"""
Snippet that compares the performance of valcheck to other data-validation libraries.
Versions used: Please refer to the `requirements_for_performance_testing.txt` file
"""


from datetime import date
import functools
import time
from typing import Any, Dict, Literal

import pydantic
from rest_framework import serializers

from valcheck import fields, models, validators


DictionaryType = Dict[str, Any]
DATE_FORMAT = "%Y-%m-%d"
NUM_REPITITIONS = 25_000


def repeat(*, num_times):
    """Decorator that executes the decorated function `num_times` times"""
    assert isinstance(num_times, int) and num_times >= 1, "Param `num_times` must be an integer which is >= 1"
    def repeat_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Running function `{func.__name__}` for {num_times} iterations")
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
        print(f"Executed `{func.__name__}` in: {time_taken_in_secs} seconds")
        return result
    return wrapper_timer


class PersonPydantic(pydantic.BaseModel):
    name: str
    age: int
    gender: Literal["Female", "Male"]
    dob: date


class PersonDjangoRestFramework(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=("Female", "Male"))
    dob = serializers.DateField(format=DATE_FORMAT)


class PersonValcheck(validators.Validator):
    name = fields.StringField(
        allow_empty=False,
        error=models.Error(description="The name should include first and last name. Eg: `Sundar Pichai`"),
        validators=[
            lambda value: len(str(value).split(" ")) >= 2,
        ],
    )
    age = fields.IntegerField(
        validators=[lambda age: age >= 18],
        error=models.Error(description="The person must be an adult (at least 18 years old)"),
    )
    gender = fields.ChoiceField(choices=("Female", "Male"))
    dob = fields.DateStringField(format_=DATE_FORMAT)


@timer
@repeat(num_times=NUM_REPITITIONS)
def pydantic_validator(data: DictionaryType) -> DictionaryType:
    result = {
        "validated_data": None,
        "errors": None,
    }
    try:
        validated_data = PersonPydantic(**data).model_dump()
        result["validated_data"] = validated_data
    except pydantic.ValidationError as exc:
        result["errors"] = exc.errors()
    return result


@timer
@repeat(num_times=NUM_REPITITIONS)
def django_rest_framework_validator(data: DictionaryType) -> DictionaryType:
    result = {
        "validated_data": None,
        "errors": None,
    }
    ser = PersonDjangoRestFramework(data=data)
    if ser.is_valid():
        result["validated_data"] = ser.validated_data
    else:
        result["errors"] = ser.errors
    return result


@timer
@repeat(num_times=NUM_REPITITIONS)
def valcheck_validator(data: DictionaryType) -> DictionaryType:
    result = {
        "validated_data": None,
        "errors": None,
    }
    person_validator = PersonValcheck(data=data)
    errors = person_validator.run_validations()
    if errors:
        result["errors"] = [error.as_dict() for error in errors]
    else:
        result["validated_data"] = person_validator.validated_data
    return result


def main():
    valid_data = {"name": "james murphy", "age": 30, "gender": "Male", "dob": "2000-01-16"}
    pydantic_validator(valid_data)
    # django_rest_framework_validator(valid_data)  # must be used inside a Django project for it to run
    valcheck_validator(valid_data)

    invalid_data = {"name": 123, "age": "hello", "gender": "haha", "dob": "2000-01-16 --"}
    pydantic_validator(invalid_data)
    # django_rest_framework_validator(invalid_data)  # must be used inside a Django project for it to run
    valcheck_validator(invalid_data)


if __name__ == "__main__":
    main()
