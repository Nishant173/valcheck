from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, Union

from valcheck.exceptions import MissingFieldException, ValidationException
from valcheck.fields import BaseField, ListOfModelsField
from valcheck.models import Error
from valcheck.utils import (
    is_empty,
    set_as_empty,
    wrap_in_quotes_if_string,
)


def _validate_list_of_models_field(
        *,
        model: Type[BaseValidator],
        field_name: str,
        field_type: str,
        field_value: Any,
        allow_empty: Optional[bool] = True,
    ) -> List[Error]:
    """Returns list of errors (each of type `valcheck.models.Error`). Will be an empty list if there are no errors"""
    assert model is not BaseValidator and issubclass(model, BaseValidator), (
        "Param `model` must be a sub-class of `valcheck.base_validator.BaseValidator`"
    )
    errors: List[Error] = []
    if not isinstance(field_value, list):
        base_error = Error()
        base_error.validator_message = f"Invalid {field_type} '{field_name}' - Field is not a list"
        errors.append(base_error)
        raise ValidationException(errors=errors)
    if not allow_empty and not field_value:
        base_error = Error()
        base_error.validator_message = f"Invalid {field_type} '{field_name}' - Field is an empty list"
        errors.append(base_error)
        raise ValidationException(errors=errors)
    for idx, item in enumerate(field_value):
        row_number = idx + 1
        if not isinstance(item, dict):
            base_error = Error()
            base_error.validator_message = f"Invalid {field_type} '{field_name}' - Row is not a dictionary"
            base_error.details.update(row_number=row_number)
            errors.append(base_error)
            continue
        try:
            model(data=item).run_validations()
        except ValidationException as exc:
            for error_item in exc.errors:
                error_item.validator_message = f"Invalid {field_type} '{field_name}' - {error_item.validator_message}"
                error_item.details.update(row_number=row_number)
            errors.extend(exc.errors)
    return errors


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

    def _perform_field_validation_checks(
            self,
            *,
            field: str,
            field_validator_instance: BaseField,
        ) -> None:
        """Performs validation checks for the given field, and registers errors (if any) and validated data"""
        required = field_validator_instance.required
        error = field_validator_instance.error
        default_func = field_validator_instance.default_func
        default_value = default_func() if default_func is not None and not required else set_as_empty()
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
            errors = _validate_list_of_models_field(
                model=field_validator_instance.model,
                field_name=field,
                field_type=field_type,
                field_value=field_validator_instance.field_value,
                allow_empty=field_validator_instance.allow_empty,
            )
            if errors:
                self._unregister_validated_data(field=field)
                self._register_errors(errors=errors)
                return
        return None

    def _perform_model_validation_checks(self) -> None:
        """Performs model validation checks, and registers errors (if any)"""
        error = self.model_validator()
        assert error is None or isinstance(error, Error), (
            "Output of model validator method should be either a NoneType or an instance of `valcheck.models.Error`"
        )
        if error is None:
            return None
        INVALID_MODEL_ERROR_MESSAGE = "Invalid model - Validation failed"
        self._assign_validator_message_to_error(error=error, validator_message=INVALID_MODEL_ERROR_MESSAGE)
        self._register_error(error=error)
        return None

    def model_validator(self) -> Union[Error, None]:
        """Output of model validator method should be either a NoneType or an instance of `valcheck.models.Error`"""
        return None

    def run_validations(self) -> None:
        """
        Runs validations and registers errors (if any) and validated data.
        Raises `valcheck.exceptions.ValidationException` if data validation fails.
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
        if self._errors:
            raise ValidationException(errors=self._errors)
        return None

    def list_field_validators(self) -> List[Dict[str, Any]]:
        return [
            {
                "field_type": field_validator_instance.__class__.__name__,
                "field_name": field,
            } for field, field_validator_instance in self._field_validators_dict.items()
        ]

