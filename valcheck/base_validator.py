from typing import Any, Callable, Dict, List, Optional

from valcheck.errors import ValidationError
from valcheck.fields import BaseField
from valcheck.models import Error
from valcheck.utils import (
    is_empty,
    set_as_empty,
    wrap_in_quotes_if_string,
)


class BaseValidator:
    """
    Exposed properties:
        - errors
        - errors_as_list_of_dicts
        - validated_data

    Exposed methods:
        - is_valid()
        - list_validators()
    """
    def __init__(self, *, data: Dict[str, Any]) -> None:
        assert isinstance(data, dict), "Param `data` must be a dictionary"
        self.data = data
        self._field_validators_dict: Dict[str, BaseField] = self._get_field_validators_dict()
        self._model_validators: List[Callable] = self._get_model_validators()
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

    def _get_model_validators(self) -> List[Callable]:
        """Returns list of model validators (callables). Used to validate the entire model"""
        return [
            validator_func for _, validator_func  in vars(self.__class__).items() if callable(validator_func)
        ]

    @property
    def errors(self) -> List[Error]:
        return self._errors

    @property
    def errors_as_list_of_dicts(self) -> List[Dict[str, Any]]:
        return [error.as_dict() for error in self.errors]

    def _clear_errors(self) -> None:
        """Clears out the list of errors"""
        self._errors.clear()

    def _register_error(self, error: Error) -> None:
        self._errors.append(error)

    def _assign_validator_message_to_error(self, *, error: Error, validator_message: str) -> None:
        error.validator_message = validator_message

    def _register_validated_data(self, field: str, field_value: Any) -> None:
        self._validated_data[field] = field_value

    def _unregister_validated_data(self, field: str) -> None:
        self._validated_data.pop(field, None)

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def _clear_validated_data(self) -> None:
        """Clears out the dictionary having validated data"""
        self._validated_data.clear()

    def _perform_field_validation_checks(
            self,
            *,
            field: str,
            field_validator_instance: BaseField,
        ) -> None:
        """Performs validation checks for the given field, and registers errors (if any)"""
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
        return None

    def _perform_model_validation_checks(self, *, model_validator: Callable) -> None:
        """Performs validation checks for the given `model_validator`, and registers errors (if any)"""
        error = model_validator(self._validated_data.copy())
        assert error is None or isinstance(error, Error), (
            "Output of model validator functions should be either a NoneType or an instance of `valcheck.models.Error`"
        )
        if error is None:
            return None
        INVALID_MODEL_ERROR_MESSAGE = f"Invalid model due to failed validation in `{model_validator.__name__}()`"
        self._assign_validator_message_to_error(error=error, validator_message=INVALID_MODEL_ERROR_MESSAGE)
        self._register_error(error=error)
        return None

    def _raise_exception_if_needed(self, raise_exception: bool, many: bool) -> None:
        """Raises `ValidationError` if needed"""
        if raise_exception and self.errors:
            errors = self.errors_as_list_of_dicts
            raise ValidationError(error_info=errors) if many else ValidationError(error_info=errors[0])

    def is_valid(
            self,
            *,
            raise_exception: Optional[bool] = False,
            many: Optional[bool] = True,
        ) -> bool:
        """Returns boolean. If `raise_exception=True` and data validation fails, then raises `ValidationError`"""
        self._clear_errors()
        self._clear_validated_data()
        for field, field_validator_instance in self._field_validators_dict.items():
            self._perform_field_validation_checks(
                field=field,
                field_validator_instance=field_validator_instance,
            )
        # Perform model validator checks only if there are no errors in field validator checks
        if not self.errors:
            for model_validator in self._model_validators:
                self._perform_model_validation_checks(model_validator=model_validator)
        self._raise_exception_if_needed(raise_exception=raise_exception, many=many)
        return False if self.errors else True

    def list_validators(self) -> List:
        validators = []
        for field, field_validator_instance in self._field_validators_dict.items():
            validators.append({
                "type": "Field-Validator",
                "subtype": field_validator_instance.__class__.__name__,
                "name": field,
            })
        for model_validator in self._model_validators:
            validators.append({
                "type": "Model-Validator",
                "subtype": None,
                "name": model_validator.__name__,
            })
        return validators

