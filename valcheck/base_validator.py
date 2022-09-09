from typing import Any, Callable, Dict, List, Optional

from valcheck.errors import ValidationError
from valcheck.fields import BaseField
from valcheck.models import Error
from valcheck.utils import (
    is_empty,
    set_as_empty,
)


class BaseValidator:
    def __init__(
            self,
            *,
            data: Optional[Dict[str, Any]] = None,
        ) -> None:
        if data is not None:
            assert isinstance(data, dict), "Param `data` must be a dictionary"
        self.data = set_as_empty() if data is None else data
        self._field_validators_dict = self._get_field_validators_dict()
        self._model_validators = self._get_model_validators()
        self._errors = []
        self._validated_data = {}

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

    @staticmethod
    def _wrap_in_quotes_if_string(obj: Any) -> str:
        if isinstance(obj, str):
            return f"'{obj}'"
        return f"{obj}"

    @property
    def errors(self) -> List[Dict[str, Any]]:
        return self._errors

    def clear_errors(self) -> None:
        """Clears out the list of errors"""
        self._errors = []

    def _update_error_kwargs(
            self,
            error_kwargs: Dict[str, Any],
            kwarg: Dict[str, Any],
        ) -> None:
        """Updates the `error_kwargs` dictionary with the `kwarg` given (in-place)"""
        error_kwargs.update(**kwarg)

    def _register_error(self, error_kwargs: Dict[str, Any]) -> None:
        self._errors.append(Error(**error_kwargs).as_dict())

    def _register_validated_data(self, field: str, field_value: Any) -> None:
        if not is_empty(field_value):
            self._validated_data[field] = field_value

    def _unregister_validated_data(self, field: str) -> None:
        self._validated_data.pop(field, None)

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def clear_validated_data(self) -> None:
        """Clears out the dictionary having validated data"""
        self._validated_data = {}

    def _ensure_validator_message_is_missing(self, error_kwargs: Dict[str, Any]) -> None:
        """Ensures that the kwarg 'validator_message' is not passed in `error_kwargs`, as this will be set by `BaseValidator`"""
        assert ('validator_message' not in error_kwargs), (
            "The param `error_kwargs` must not have the kwarg 'validator_message', as this will be set by `BaseValidator`"
        )

    def _perform_field_validation_checks(
            self,
            *,
            field: str,
            field_validator_instance: BaseField,
        ) -> None:
        """Performs validation checks for the given field, and registers errors (if any)"""
        required = field_validator_instance.required
        error_kwargs = field_validator_instance.error_kwargs
        default_func = field_validator_instance.default_func
        default_value = default_func() if default_func is not None and not required else set_as_empty()
        self._ensure_validator_message_is_missing(error_kwargs=error_kwargs)
        field_type = field_validator_instance.__class__.__name__
        field_value = self.data.get(field, default_value)
        MISSING_FIELD_ERROR_MESSAGE = f"Missing {field_type} '{field}'"
        INVALID_FIELD_ERROR_MESSAGE = f"Invalid {field_type} '{field}' having value {self._wrap_in_quotes_if_string(field_value)}"
        self._register_validated_data(field=field, field_value=field_value)
        if is_empty(field_value) and required:
            self._unregister_validated_data(field=field)
            self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'validator_message': MISSING_FIELD_ERROR_MESSAGE})
            self._register_error(error_kwargs=error_kwargs)
            return
        if is_empty(field_value) and not required:
            self._unregister_validated_data(field=field)
            return
        field_validator_instance.field_value = field_value
        if not field_validator_instance.is_valid():
            self._unregister_validated_data(field=field)
            self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'validator_message': INVALID_FIELD_ERROR_MESSAGE})
            self._register_error(error_kwargs=error_kwargs)
            return
        return None

    def _perform_model_validation_checks(self, *, model_validator: Callable) -> None:
        """Performs validation checks for the given `model_validator`, and registers errors (if any)"""
        error_kwargs = model_validator(self._validated_data.copy())
        assert (error_kwargs is None or isinstance(error_kwargs, dict)), (
            "Output of model validator functions should be either NoneType or a dictionary having error kwargs"
        )
        if error_kwargs is None:
            return None
        self._ensure_validator_message_is_missing(error_kwargs=error_kwargs)
        INVALID_MODEL_ERROR_MESSAGE = f"Invalid model due to failed validation in `{model_validator.__name__}()`"
        self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'validator_message': INVALID_MODEL_ERROR_MESSAGE})
        self._register_error(error_kwargs=error_kwargs)
        return None

    def _raise_exception_if_needed(self, raise_exception: bool, many: bool) -> None:
        """Raises `ValidationError` if needed"""
        if raise_exception and self.errors:
            raise ValidationError(error_info=self.errors) if many else ValidationError(error_info=self.errors[0])

    def is_valid(
            self,
            *,
            raise_exception: Optional[bool] = False,
            many: Optional[bool] = True,
        ) -> bool:
        """Returns boolean. If `raise_exception=True` and data validation fails, then raises `ValidationError`"""
        assert isinstance(self.data, dict), "Cannot call `is_valid()` without setting the `data` dictionary"
        self.clear_errors()
        self.clear_validated_data()
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

