from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type

from valcheck.exceptions import MissingFieldException, ValidationException
from valcheck.fields import BaseField, DictionaryOfModelField, ListOfModelsField
from valcheck.models import Error
from valcheck.utils import (
    is_empty,
    is_list_of_instances_of_type,
    set_as_empty,
    wrap_in_quotes_if_string,
)


def _validate_dictionary_of_model_field(
        *,
        validator_model: Type[BaseValidator],
        field_name: str,
        field_type: str,
        field_value: Any,
    ) -> Tuple[List[Error], Dict[str, Any]]:
    """
    Returns tuple having (errors, validated_data).
    Param `errors` will be a list of errors (each of type `valcheck.models.Error`). Will be an empty list if there are no errors.
    Param `validated_data` will contain the validated data for this field.
    """
    assert validator_model is not BaseValidator and issubclass(validator_model, BaseValidator), (
        "Param `validator_model` must be a sub-class of `valcheck.base_validator.BaseValidator`"
    )
    validated_data = {}
    if not isinstance(field_value, dict):
        error = Error()
        error.validator_message = f"Invalid {field_type} '{field_name}' - Field is not a dictionary"
        return ([error], validated_data)
    validator = validator_model(data=field_value)
    error_objs = validator.run_validations()
    if not error_objs:
        validated_data.update(**validator.validated_data)
    for error_obj in error_objs:
        error_obj.validator_message = f"Invalid {field_type} '{field_name}' - {error_obj.validator_message}"
    return (error_objs, validated_data)


def _validate_list_of_models_field(
        *,
        validator_model: Type[BaseValidator],
        field_name: str,
        field_type: str,
        field_value: Any,
        allow_empty: Optional[bool] = True,
    ) -> Tuple[List[Error], List[Any]]:
    """
    Returns tuple having (errors, validated_data).
    Param `errors` will be a list of errors (each of type `valcheck.models.Error`). Will be an empty list if there are no errors.
    Param `validated_data` will contain the validated data for this field.
    """
    assert validator_model is not BaseValidator and issubclass(validator_model, BaseValidator), (
        "Param `validator_model` must be a sub-class of `valcheck.base_validator.BaseValidator`"
    )
    validated_data = []
    if not isinstance(field_value, list):
        error = Error()
        error.validator_message = f"Invalid {field_type} '{field_name}' - Field is not a list"
        return ([error], validated_data)
    if not allow_empty and not field_value:
        error = Error()
        error.validator_message = f"Invalid {field_type} '{field_name}' - Field is an empty list"
        return ([error], validated_data)
    errors: List[Error] = []
    for idx, item in enumerate(field_value):
        row_number = idx + 1
        if not isinstance(item, dict):
            error = Error()
            error.validator_message = f"Invalid {field_type} '{field_name}' - Row is not a dictionary"
            error.details.update(row_number=row_number)
            errors.append(error)
            continue
        validator = validator_model(data=item)
        error_objs = validator.run_validations()
        if not error_objs:
            validated_data.append(validator.validated_data)
        for error_obj in error_objs:
            error_obj.validator_message = f"Invalid {field_type} '{field_name}' - {error_obj.validator_message}"
            error_obj.details.update(row_number=row_number)
        errors.extend(error_objs)
    if errors:
        validated_data.clear()
    return (errors, validated_data)


class BaseValidator:
    """
    Properties:
        - validated_data

    Instance methods:
        - get_field_value()
        - list_field_validators()
        - model_validator()
        - run_validations()
    """

    def __init__(self, *, data: Dict[str, Any]) -> None:
        assert isinstance(data, dict), "Param `data` must be a dictionary"
        self.data = data
        self._field_validators_dict: Dict[str, BaseField] = self._get_field_validators_dict()
        self._errors: List[Error] = []
        self._validated_data: Dict[str, Any] = {}

    def _get_field_validators_dict(self) -> Dict[str, BaseField]:
        """Returns dictionary having keys = field names, and values = field validator instances"""
        return {
            field_name : field_validator_instance for field_name, field_validator_instance in vars(self.__class__).items() if (
                not field_name.startswith("__")
                and isinstance(field_name, str)
                and field_validator_instance.__class__ is not BaseField
                and issubclass(field_validator_instance.__class__, BaseField)
            )
        }

    def _clear_errors(self) -> None:
        """Clears out the list of errors"""
        self._errors.clear()

    def _register_error(self, error: Error) -> None:
        self._errors.append(error)

    def _register_errors(self, errors: List[Error]) -> None:
        self._errors.extend(errors)

    def _assign_validator_message_to_error(self, *, error: Error, validator_message: str) -> None:
        error.validator_message = validator_message

    def _register_validated_data(self, field: str, field_value: Any) -> None:
        self._validated_data[field] = field_value

    def _unregister_validated_data(self, field: str) -> None:
        self._validated_data.pop(field, None)

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def get_field_value(self, field: str, /) -> Any:
        """Returns the validated field value. Raises `valcheck.exceptions.MissingFieldException` if the field is missing"""
        if field in self.validated_data:
            return self.validated_data[field]
        raise MissingFieldException(f"The field '{field}' is missing from the validated data")

    def _clear_validated_data(self) -> None:
        """Clears out the dictionary having validated data"""
        self._validated_data.clear()

    def _handle_list_of_models_field(self, *, field_name: str, field_type: str, field_validator_instance: ListOfModelsField) -> None:
        errors, validated_data = _validate_list_of_models_field(
            validator_model=field_validator_instance.validator_model,
            field_name=field_name,
            field_type=field_type,
            field_value=field_validator_instance.field_value,
            allow_empty=field_validator_instance.allow_empty,
        )
        self._unregister_validated_data(field=field_name)
        if errors:
            self._register_errors(errors=errors)
        else:
            self._register_validated_data(field=field_name, field_value=validated_data)

    def _handle_dictionary_of_model_field(self, *, field_name: str, field_type: str, field_validator_instance: DictionaryOfModelField) -> None:
        errors, validated_data = _validate_dictionary_of_model_field(
            validator_model=field_validator_instance.validator_model,
            field_name=field_name,
            field_type=field_type,
            field_value=field_validator_instance.field_value,
        )
        self._unregister_validated_data(field=field_name)
        if errors:
            self._register_errors(errors=errors)
        else:
            self._register_validated_data(field=field_name, field_value=validated_data)

    def _perform_field_validation_checks(
            self,
            *,
            field: str,
            field_validator_instance: BaseField,
        ) -> None:
        """Performs validation checks for the given field, and registers errors (if any) and validated data"""
        required = field_validator_instance.required
        error = field_validator_instance.error
        default_factory = field_validator_instance.default_factory
        default_value = default_factory() if default_factory is not None and not required else set_as_empty()
        field_type = field_validator_instance.__class__.__name__
        field_value = self.data.get(field, default_value)
        MISSING_FIELD_ERROR_MESSAGE = f"Missing {field_type} '{field}'"
        INVALID_FIELD_ERROR_MESSAGE = f"Invalid {field_type} '{field}' having value {wrap_in_quotes_if_string(field_value)}"
        self._register_validated_data(field=field, field_value=field_value)
        if is_empty(field_value) and required:
            self._unregister_validated_data(field=field)
            self._assign_validator_message_to_error(error=error, validator_message=MISSING_FIELD_ERROR_MESSAGE)
            self._register_error(error=error)
            return
        if is_empty(field_value) and not required:
            self._unregister_validated_data(field=field)
            return
        field_validator_instance.field_value = field_value
        if not field_validator_instance.is_valid():
            self._unregister_validated_data(field=field)
            self._assign_validator_message_to_error(error=error, validator_message=INVALID_FIELD_ERROR_MESSAGE)
            self._register_error(error=error)
            return
        if isinstance(field_validator_instance, ListOfModelsField):
            self._handle_list_of_models_field(field_name=field, field_type=field_type, field_validator_instance=field_validator_instance)
        if isinstance(field_validator_instance, DictionaryOfModelField):
            self._handle_dictionary_of_model_field(field_name=field, field_type=field_type, field_validator_instance=field_validator_instance)
        return None

    def _perform_model_validation_checks(self) -> None:
        """Performs model validation checks, and registers errors (if any)"""
        errors = self.model_validator()
        assert is_list_of_instances_of_type(errors, type_=Error, allow_empty=True), (
            "The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`)."
            " Must be an empty list if there are no errors."
        )
        INVALID_MODEL_ERROR_MESSAGE = "Invalid model - Validation failed"
        for error in errors:
            self._assign_validator_message_to_error(error=error, validator_message=INVALID_MODEL_ERROR_MESSAGE)
        self._register_errors(errors=errors)
        return None

    def model_validator(self) -> List[Error]:
        """
        The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        return []

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> List[Error]:
        """
        Runs validations and registers errors / validated data. Returns list of errors.
        If `raise_exception=True` and validations fail, raises `valcheck.exceptions.ValidationException`.
        """
        self._clear_errors()
        self._clear_validated_data()
        for field, field_validator_instance in self._field_validators_dict.items():
            self._perform_field_validation_checks(
                field=field,
                field_validator_instance=field_validator_instance,
            )
        # Perform model validation checks only if there are no errors in field validation checks
        if not self._errors:
            self._perform_model_validation_checks()
        if raise_exception and self._errors:
            raise ValidationException(errors=self._errors)
        return self._errors

    def list_field_validators(self) -> List[Dict[str, Any]]:
        return [
            {
                "field_type": field_validator_instance.__class__.__name__,
                "field_name": field,
            } for field, field_validator_instance in self._field_validators_dict.items()
        ]

