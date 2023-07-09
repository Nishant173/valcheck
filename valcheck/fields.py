from __future__ import annotations

from typing import Any, Callable, Iterable, List, Optional, Type, Union

from valcheck.models import Error
from valcheck.utils import (
    Empty,
    dict_has_any_keys,
    is_empty,
    is_instance_of_any,
    is_iterable,
    is_list_of_instances_of_type,
    is_valid_datetime_string,
    is_valid_email_id,
    is_valid_json_string,
    is_valid_object_of_type,
    is_valid_uuid_string,
    set_as_empty,
)


def _invalid_field_error(field: Field, /, *, prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    return (
        f"{prefix if prefix else ''}"
        f"Invalid {field.__class__.__name__} '{field.field_name}'"
        f"{suffix if suffix else ''}"
    )


def _missing_field_error(field: Field, /, *, prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
    return (
        f"{prefix if prefix else ''}"
        f"Missing {field.__class__.__name__} '{field.field_name}'"
        f"{suffix if suffix else ''}"
    )


def _assign_error_in_invalid_field(field: Field, /) -> None:
    """Updates the given field's error object (in-place) for invalid field errors"""
    field.error.validator_message = _invalid_field_error(field)
    field.error.append_to_field_path(field.field_name)


class ValidatedField:
    """Class that represents a validated field"""

    def __init__(
            self,
            *,
            field_name: str,
            field_value: Union[Any, Empty],
            errors: List[Error],
        ) -> None:
        assert isinstance(field_name, str), "Param `field_name` must be of type 'str'"
        assert is_list_of_instances_of_type(errors, type_=Error, allow_empty=True), (
            "Param `errors` must be a list where each item is of type `valcheck.models.Error`"
        )

        self.field_name = field_name
        self._field_value = field_value
        self._errors = errors

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(field_name='{self.field_name}')"

    @property
    def field_value(self) -> Union[Any, Empty]:
        return self._field_value

    @field_value.setter
    def field_value(self, value: Union[Any, Empty]) -> None:
        self._field_value = value

    @property
    def errors(self) -> List[Error]:
        return self._errors

    @errors.setter
    def errors(self, value: List[Error]) -> None:
        assert is_list_of_instances_of_type(value, type_=Error, allow_empty=True), (
            "Param `errors` must be a list where each item is of type `valcheck.models.Error`"
        )
        self._errors = value


class Field:
    """Class that represents a field (that needs to be validated)"""

    def __init__(
            self,
            *,
            required: Optional[bool] = True,
            nullable: Optional[bool] = False,
            default_factory: Optional[Callable] = None,
            converter_factory: Optional[Callable] = None,
            validators: Optional[List[Callable]] = None,
            error: Optional[Error] = None,
        ) -> None:
        """
        Parameters:
            - required (bool): True if the field is required, else False. Default: True
            - nullable (bool): True if the field is nullable, else False. Default: False
            - default_factory (callable): Callable that returns the default value to set for the field
            if `required=False` and the field is missing.
            - converter_factory (callable): Callable that takes in the validated value (of the field), and returns
            the converted value (for the field).
            - validators (list of callables): List of callables that each return a boolean (takes the field value as a param).
            The callable returns True if validation is successful, else False.
            - error (Error instance): Instance of type `valcheck.models.Error`.
        """
        assert isinstance(required, bool), "Param `required` must be of type 'bool'"
        assert isinstance(nullable, bool), "Param `nullable` must be of type 'bool'"
        assert default_factory is None or callable(default_factory), (
            "Param `default_factory` must be a callable that returns the default value if the field is missing when `required=False`"
        )
        assert converter_factory is None or callable(converter_factory), (
            "Param `converter_factory` must be a callable that takes in the validated value (of the field), and returns"
            " the converted value (for the field)."
        )
        assert validators is None or isinstance(validators, list), "Param `validators` must be of type 'list'"
        if isinstance(validators, list):
            for validator in validators:
                assert callable(validator), "Param `validators` must be a list of callables"
        assert error is None or isinstance(error, Error), "Param `error` must be of type `valcheck.models.Error`"

        self._field_name = set_as_empty()
        self._field_value = set_as_empty()
        self.required = required
        self.nullable = nullable
        self.default_factory = default_factory
        self.converter_factory = converter_factory
        self.validators = validators or []
        self.error = error or Error()

    @property
    def field_name(self) -> str:
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        assert isinstance(value, str), "Param `field_name` must be of type 'str'"
        self._field_name = value

    @property
    def field_value(self) -> Any:
        return self._field_value

    @field_value.setter
    def field_value(self, value: Any) -> None:
        self._field_value = value

    def _can_be_set_to_null(self) -> bool:
        return self.nullable and self.field_value is None

    def _has_valid_custom_validators(self) -> bool:
        if not self.validators:
            return True
        validator_return_values = [validator(self.field_value) for validator in self.validators]
        for return_value in validator_return_values:
            assert isinstance(return_value, bool), (
                f"Expected the return type of `validators` to be 'bool', but got '{type(return_value).__name__}'"
            )
        return all(validator_return_values)

    def _convert_field_value_if_needed(self) -> Any:
        """Returns the converted field value if a `converter_factory` is present; otherwise returns the same field value"""
        return self.converter_factory(self.field_value) if self.converter_factory else self.field_value

    def validate(self) -> List[Error]:
        """Returns list of errors (each of type `valcheck.models.Error`)"""
        raise NotImplementedError()

    def run_validations(self) -> ValidatedField:
        error_obj = self.error.copy()
        if is_empty(self.field_value) and not self.required and self.default_factory:
            self.field_value = self.default_factory()
        validated_field = ValidatedField(
            field_name=self.field_name,
            field_value=self.field_value,
            errors=[],
        )
        if is_empty(self.field_value) and not self.required and not self.default_factory:
            return validated_field
        if self._can_be_set_to_null():
            validated_field.field_value = self._convert_field_value_if_needed()
            return validated_field
        if is_empty(self.field_value) and self.required:
            error_obj.validator_message = _missing_field_error(self)
            error_obj.append_to_field_path(self.field_name)
            validated_field.errors += [error_obj]
            return validated_field
        errors = self.validate()
        if errors:
            validated_field.errors += errors
            return validated_field
        if not self._has_valid_custom_validators():
            error_obj.validator_message = _invalid_field_error(self)
            error_obj.append_to_field_path(self.field_name)
            validated_field.errors += [error_obj]
            return validated_field
        validated_field.field_value = self._convert_field_value_if_needed()
        return validated_field



class AnyField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(AnyField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        return []


class BooleanField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(BooleanField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, bool):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class StringField(Field):

    def __init__(self, *, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        self.allow_empty = allow_empty
        super(StringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if is_valid_object_of_type(self.field_value, type_=str, allow_empty=self.allow_empty):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class JsonStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(JsonStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and is_valid_json_string(self.field_value):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class EmailIdField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(EmailIdField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and is_valid_email_id(self.field_value):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class UuidStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(UuidStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and is_valid_uuid_string(self.field_value):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class DateStringField(Field):
    def __init__(self, *, format_: Optional[str] = "%Y-%m-%d", **kwargs: Any) -> None:
        self.format_ = format_
        super(DateStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and is_valid_datetime_string(self.field_value, self.format_):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class DatetimeStringField(Field):
    def __init__(self, *, format_: Optional[str] = "%Y-%m-%d %H:%M:%S", **kwargs: Any) -> None:
        self.format_ = format_
        super(DatetimeStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and is_valid_datetime_string(self.field_value, self.format_):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class ChoiceField(Field):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(ChoiceField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if self.field_value in self.choices:
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class MultiChoiceField(Field):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(MultiChoiceField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if (
            isinstance(self.field_value, list)
            and all([item in self.choices for item in self.field_value])
        ):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class BytesField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(BytesField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, bytes):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class NumberField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(NumberField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if is_instance_of_any(obj=self.field_value, types=[int, float]):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class IntegerField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(IntegerField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, int):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class FloatField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(FloatField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, float):
            return []
        _assign_error_in_invalid_field(self)
        return [self.error]


class ModelDictionaryField(Field):
    def __init__(self, *, validator_model: Type, **kwargs: Any) -> None:
        from valcheck.validator import Validator
        assert validator_model is not Validator and issubclass(validator_model, Validator), (
            "Param `validator_model` must be a sub-class of `valcheck.validator.Validator`"
        )
        kwargs_to_disallow = ['validators', 'error']
        if dict_has_any_keys(kwargs, keys=kwargs_to_disallow):
            msg = (
                f"This field does not accept the following params: {kwargs_to_disallow}, since"
                " the `validator_model` handles these parameters"
            )
            raise ValueError(msg)
        self.validator_model = validator_model
        super(ModelDictionaryField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if not isinstance(self.field_value, dict):
            error = Error()
            error.validator_message = _invalid_field_error(self, suffix=" - Field is not a dictionary")
            error.append_to_field_path(self.field_name)
            return [error]
        validator = self.validator_model(data=self.field_value)
        error_objs = validator.run_validations()
        for error_obj in error_objs:
            error_obj.validator_message = _invalid_field_error(self, suffix=f" - {error_obj.validator_message}")
            error_obj.append_to_field_path(self.field_name)
        if not error_objs:
            self.field_value = validator.validated_data
        return error_objs


class ModelListField(Field):
    def __init__(self, *, validator_model: Type, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        from valcheck.validator import Validator
        assert validator_model is not Validator and issubclass(validator_model, Validator), (
            "Param `validator_model` must be a sub-class of `valcheck.validator.Validator`"
        )
        kwargs_to_disallow = ['validators', 'error']
        if dict_has_any_keys(kwargs, keys=kwargs_to_disallow):
            msg = (
                f"This field does not accept the following params: {kwargs_to_disallow}, since"
                " the `validator_model` handles these parameters"
            )
            raise ValueError(msg)
        self.validator_model = validator_model
        self.allow_empty = allow_empty
        super(ModelListField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if not isinstance(self.field_value, list):
            error = Error()
            error.validator_message = _invalid_field_error(self, suffix=" - Field is not a list")
            error.append_to_field_path(self.field_name)
            return [error]
        if not self.allow_empty and not self.field_value:
            error = Error()
            error.validator_message = _invalid_field_error(self, suffix=" - Field is an empty list")
            error.append_to_field_path(self.field_name)
            return [error]
        errors: List[Error] = []
        validated_field_value = []
        for idx, item in enumerate(self.field_value):
            row_number = idx + 1
            row_number_string = f"<Row number: {row_number}>"
            if not isinstance(item, dict):
                error = Error()
                error.validator_message = _invalid_field_error(
                    self,
                    suffix=f" - Row is not a dictionary {row_number_string}",
                )
                error.append_to_field_path(self.field_name)
                errors.append(error)
                continue
            validator = self.validator_model(data=item)
            error_objs = validator.run_validations()
            validated_field_value.append(validator.validated_data)
            for error_obj in error_objs:
                error_obj.validator_message = _invalid_field_error(
                    self,
                    suffix=f" - {error_obj.validator_message} {row_number_string}",
                )
                error_obj.append_to_field_path(self.field_name)
            errors.extend(error_objs)
        if not errors:
            self.field_value = validated_field_value
        return errors

