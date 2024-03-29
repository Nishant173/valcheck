from __future__ import annotations

import copy
from typing import Any, Callable, Iterable, List, Optional, Type, Union

from valcheck.models import Error
from valcheck import utils


class ValidatedField:
    """Class that represents a validated field"""

    def __init__(
            self,
            *,
            field: Field,
            errors: List[Error],
        ) -> None:
        assert isinstance(field, Field), "Param `field` must be of type `valcheck.fields.Field`"
        assert utils.is_list_of_instances_of_type(errors, type_=Error, allow_empty=True), (
            "Param `errors` must be a list where each item is of type `valcheck.models.Error`"
        )
        self._field = field
        self._errors = errors

    def __str__(self) -> str:
        kwargs_list = [
            f"is_valid={not bool(self.errors)}",
            f"field_identifier={utils.wrap_in_quotes_if_string(self.field.field_identifier)}",
            f"field_value={utils.wrap_in_quotes_if_string(self.field.field_value)}",
            f"source={utils.wrap_in_quotes_if_string(self.field.source)}",
            f"target={utils.wrap_in_quotes_if_string(self.field.target)}",
            f"required={self.field.required}",
            f"nullable={self.field.nullable}",
            f"type_alias={utils.wrap_in_quotes_if_string(self.field.type_alias)}",
        ]
        kwargs_string = "(" + ", ".join(kwargs_list) + ")"
        return f"{self.__class__.__name__}{kwargs_string}"

    @property
    def field(self) -> Field:
        return self._field

    @field.setter
    def field(self, value: Field) -> None:
        assert isinstance(value, Field), "Param `field` must be of type `valcheck.fields.Field`"
        self._field = value

    @property
    def errors(self) -> List[Error]:
        return self._errors

    @errors.setter
    def errors(self, value: List[Error]) -> None:
        assert utils.is_list_of_instances_of_type(value, type_=Error, allow_empty=True), (
            "Param `errors` must be a list where each item is of type `valcheck.models.Error`"
        )
        self._errors = value


class Field:
    """Class that represents a field (that needs to be validated)"""

    def __init__(
            self,
            *,
            source: Optional[str] = None,
            target: Optional[str] = None,
            required: Optional[bool] = True,
            nullable: Optional[bool] = False,
            default_factory: Optional[Callable] = None,
            converter_factory: Optional[Callable] = None,
            validators: Optional[List[Callable]] = None,
            error: Optional[Error] = None,
            type_alias: Optional[str] = None,
        ) -> None:
        """
        Parameters:
            - source (str): Field name used in the input data (optional)
            - target (str): Field name used in the validated data (optional)
            - required (bool): True if the field is required, else False. Default: True
            - nullable (bool): True if the field is nullable, else False. Default: False
            - default_factory (callable): Callable that returns the default value to set for the field
            if `required=False` and the field is missing.
            - converter_factory (callable): Callable that takes in the validated value (of the field), and returns
            the converted value (for the field).
            - validators (list of callables): List of callables that each return a boolean (takes the field value as a param).
            The callable returns True if validation is successful, else False.
            - error (Error instance): Instance of type `valcheck.models.Error`.
            - type_alias (str): Alias of the field type (optional).
        """
        assert source is None or utils.is_valid_object_of_type(source, type_=str, allow_empty=False), (
            "Param `source` must be of type 'str' and must be non-empty"
        )
        assert target is None or utils.is_valid_object_of_type(target, type_=str, allow_empty=False), (
            "Param `target` must be of type 'str' and must be non-empty"
        )
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
        assert type_alias is None or utils.is_valid_object_of_type(type_alias, type_=str, allow_empty=False), (
            "Param `type_alias` must be of type 'str' and must be non-empty"
        )

        self._field_identifier = utils.set_as_empty()
        self._field_value = utils.set_as_empty()
        self.source = source
        self.target = target
        self.required = required
        self.nullable = nullable
        self.default_factory = default_factory
        self.converter_factory = converter_factory
        self.validators = validators or []
        self.error = error or Error()
        self.type_alias = type_alias or self.__class__.__name__

    def copy(self) -> Field:
        """Returns deep-copy of current `Field` object"""
        return copy.deepcopy(self)

    def __str__(self) -> str:
        kwargs_list = [
            f"field_identifier={utils.wrap_in_quotes_if_string(self.field_identifier)}",
            f"field_value={utils.wrap_in_quotes_if_string(self.field_value)}",
            f"source={utils.wrap_in_quotes_if_string(self.source)}",
            f"target={utils.wrap_in_quotes_if_string(self.target)}",
            f"required={self.required}",
            f"nullable={self.nullable}",
            f"type_alias={utils.wrap_in_quotes_if_string(self.type_alias)}",
        ]
        kwargs_string = "(" + ", ".join(kwargs_list) + ")"
        return f"{self.__class__.__name__}{kwargs_string}"

    @property
    def field_identifier(self) -> str:
        return self._field_identifier

    @field_identifier.setter
    def field_identifier(self, value: str) -> None:
        assert isinstance(value, str), "Param `field_identifier` must be of type 'str'"
        self._field_identifier = value

    @property
    def field_value(self) -> Union[Any, utils.Empty]:
        return self._field_value

    @field_value.setter
    def field_value(self, value: Union[Any, utils.Empty]) -> None:
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
        if utils.is_empty(self.field_value) and not self.required and self.default_factory:
            self.field_value = self.default_factory()
        validated_field = ValidatedField(field=self, errors=[])
        if utils.is_empty(self.field_value) and not self.required and not self.default_factory:
            return validated_field
        if self._can_be_set_to_null():
            validated_field.field.field_value = self._convert_field_value_if_needed()
            return validated_field
        if utils.is_empty(self.field_value) and self.required:
            validated_field.errors += [
                self.create_error_instance(validator_message=self.missing_field_error_message()),
            ]
            return validated_field
        errors = self.validate()
        if errors:
            validated_field.errors += errors
            return validated_field
        if not self._has_valid_custom_validators():
            validated_field.errors += [
                self.create_error_instance(validator_message=self.invalid_field_error_message()),
            ]
            return validated_field
        validated_field.field.field_value = self._convert_field_value_if_needed()
        return validated_field

    def invalid_field_error_message(self, *, prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        return (
            f"{prefix if prefix else ''}"
            f"Invalid {self.type_alias} '{self.source}'"
            f"{suffix if suffix else ''}"
        )

    def missing_field_error_message(self, *, prefix: Optional[str] = None, suffix: Optional[str] = None) -> str:
        return (
            f"{prefix if prefix else ''}"
            f"Missing {self.type_alias} '{self.source}'"
            f"{suffix if suffix else ''}"
        )

    def create_error_instance(self, *, validator_message: str) -> Error:
        """Creates and returns a new `valcheck.models.Error` instance for the field"""
        error_copy = self.error.copy()
        error_copy.validator_message = validator_message
        error_copy.append_to_field_path(self.source)
        return error_copy


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
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class StringField(Field):
    def __init__(self, *, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        self.allow_empty = allow_empty
        super(StringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_object_of_type(self.field_value, type_=str, allow_empty=self.allow_empty):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class JsonStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(JsonStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and utils.is_valid_json_string(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class EmailIdField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(EmailIdField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and utils.is_valid_email_id(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class UuidStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(UuidStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and utils.is_valid_uuid_string(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class DateStringField(Field):
    def __init__(self, *, format_: Optional[str] = "%Y-%m-%d", **kwargs: Any) -> None:
        self.format_ = format_
        super(DateStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and utils.is_valid_datetime_string(self.field_value, self.format_):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class DatetimeStringField(Field):
    def __init__(self, *, format_: Optional[str] = "%Y-%m-%d %H:%M:%S", **kwargs: Any) -> None:
        self.format_ = format_
        super(DatetimeStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, str) and utils.is_valid_datetime_string(self.field_value, self.format_):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class ChoiceField(Field):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert utils.is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(ChoiceField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if self.field_value in self.choices:
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class MultiChoiceField(Field):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert utils.is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(MultiChoiceField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if (
            isinstance(self.field_value, list)
            and all([item in self.choices for item in self.field_value])
        ):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class BytesField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(BytesField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, bytes):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class NumberField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(NumberField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_instance_of_any(obj=self.field_value, types=[int, float]):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class IntegerField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(IntegerField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, int):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class FloatField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(FloatField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if isinstance(self.field_value, float):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class NumberStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(NumberStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_number_string(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class IntegerStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(IntegerStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_integer_string(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class FloatStringField(Field):
    def __init__(self, **kwargs: Any) -> None:
        super(FloatStringField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_float_string(self.field_value):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class DictionaryField(Field):
    def __init__(self, *, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        self.allow_empty = allow_empty
        super(DictionaryField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_object_of_type(self.field_value, type_=dict, allow_empty=self.allow_empty):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class ListField(Field):
    def __init__(self, *, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        self.allow_empty = allow_empty
        super(ListField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if utils.is_valid_object_of_type(self.field_value, type_=list, allow_empty=self.allow_empty):
            return []
        return [self.create_error_instance(validator_message=self.invalid_field_error_message())]


class ModelDictionaryField(Field):
    def __init__(self, *, validator_model: Type, **kwargs: Any) -> None:
        from valcheck.validators import Validator
        assert validator_model is not Validator and issubclass(validator_model, Validator), (
            "Param `validator_model` must be a sub-class of `valcheck.validators.Validator`"
        )
        kwargs_to_disallow = ['validators', 'error']
        if utils.dict_has_any_keys(kwargs, keys=kwargs_to_disallow):
            msg = (
                f"This field does not accept the following params: {kwargs_to_disallow}, since"
                " the `validator_model` handles these parameters"
            )
            raise ValueError(msg)
        self.validator_model = validator_model
        super(ModelDictionaryField, self).__init__(**kwargs)

    def validate(self) -> List[Error]:
        if not isinstance(self.field_value, dict):
            error = self.create_error_instance(
                validator_message=self.invalid_field_error_message(suffix=" - Field is not a dictionary"),
            )
            return [error]
        validator = self.validator_model(data=self.field_value)
        error_objs = validator.run_validations()
        for error_obj in error_objs:
            error_obj.validator_message = self.invalid_field_error_message(suffix=f" - {error_obj.validator_message}")
            error_obj.append_to_field_path(self.source)
        if not error_objs:
            self.field_value = validator.validated_data
        return error_objs


class ModelListField(Field):
    def __init__(self, *, validator_model: Type, allow_empty: Optional[bool] = True, **kwargs: Any) -> None:
        from valcheck.validators import Validator
        assert validator_model is not Validator and issubclass(validator_model, Validator), (
            "Param `validator_model` must be a sub-class of `valcheck.validators.Validator`"
        )
        kwargs_to_disallow = ['validators', 'error']
        if utils.dict_has_any_keys(kwargs, keys=kwargs_to_disallow):
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
            error = self.create_error_instance(
                validator_message=self.invalid_field_error_message(suffix=" - Field is not a list"),
            )
            return [error]
        if not self.allow_empty and not self.field_value:
            error = self.create_error_instance(
                validator_message=self.invalid_field_error_message(suffix=" - Field is an empty list"),
            )
            return [error]
        errors: List[Error] = []
        validated_field_value = []
        for idx, item in enumerate(self.field_value):
            row_number = idx + 1
            row_number_string = f"<Row number: {row_number}>"
            if not isinstance(item, dict):
                error = self.create_error_instance(
                    validator_message=self.invalid_field_error_message(suffix=f" - Row is not a dictionary {row_number_string}"),
                )
                errors.append(error)
                continue
            validator = self.validator_model(data=item)
            error_objs = validator.run_validations()
            validated_field_value.append(validator.validated_data)
            for error_obj in error_objs:
                error_obj.validator_message = self.invalid_field_error_message(
                    suffix=f" - {error_obj.validator_message} {row_number_string}",
                )
                error_obj.append_to_field_path(self.source)
            errors.extend(error_objs)
        if not errors:
            self.field_value = validated_field_value
        return errors

