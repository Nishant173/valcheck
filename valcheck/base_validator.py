from typing import Any, Callable, Dict, List, Optional

from valcheck.errors import ValidationError
from valcheck.fields import BaseField
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
        self._class_validators = self._get_class_validators()
        self._errors = []
        self._validated_data = {}

    def _get_field_validators_dict(self) -> Dict[str, BaseField]:
        """Returns dictionary having keys = field names, and values = field validator instances"""
        return {
            field_name : field_validator_instance for field_name, field_validator_instance in vars(self.__class__).items() if (
                not field_name.startswith("__")
                and field_name != 'Meta'
                and isinstance(field_name, str)
                and field_validator_instance.__class__ is not BaseField
                and issubclass(field_validator_instance.__class__, BaseField)
            )
        }

    def _get_class_validators(self) -> List[Callable]:
        """Returns list of class validators (callables) from the Meta class"""
        metaclass = vars(self.__class__).get('Meta', None)
        if metaclass is None:
            return []
        class_validators = getattr(metaclass, "class_validators", [])
        assert isinstance(class_validators, list), "Param `class_validators` in Meta class must be of type list"
        for class_validator in class_validators:
            assert callable(class_validator), "Param `class_validators` in Meta class must be list of callables"
        return class_validators

    @staticmethod
    def _wrap_in_quotes_if_string(obj: Any) -> str:
        if isinstance(obj, str):
            return f"'{obj}'"
        return f"{obj}"

    @property
    def errors(self) -> List[Dict[str, Any]]:
        return self._errors

    def _update_error_kwargs(
            self,
            error_kwargs: Dict[str, Any],
            kwarg: Dict[str, Any],
        ) -> None:
        """Updates the `error_kwargs` dictionary with the `kwarg` given (in-place)"""
        error_kwargs.update(**kwarg)

    def _register_error(self, error_kwargs: Dict[str, Any]) -> None:
        self._errors.append(ValidationError(**error_kwargs).as_dict())

    def _raise_exception_if_needed(
            self,
            error_kwargs: Dict[str, Any],
            raise_exception: bool,
        ) -> None:
        if raise_exception:
            raise ValidationError(**error_kwargs)

    def _register_validated_data(self, field: str, field_value: Any) -> None:
        if not is_empty(field_value):
            self._validated_data[field] = field_value

    def _unregister_validated_data(self, field: str) -> None:
        self._validated_data.pop(field, None)

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def _perform_field_validation_checks(
            self,
            *,
            field: str,
            field_validator_instance: BaseField,
            raise_exception: bool,
        ) -> None:
        """Performs validation checks for the given field, and registers/raises errors (if any)"""
        field_type = field_validator_instance.__class__.__name__
        field_value = self.data.get(field, set_as_empty())
        required = field_validator_instance.required
        error_kwargs = field_validator_instance.error_kwargs
        if 'message' in error_kwargs:
            raise ValueError(
                "The param `error_kwargs` must not have the kwarg 'message', as this will be set by `BaseValidator`"
            )
        MISSING_FIELD_ERROR_MESSAGE = f"Missing {field_type} '{field}'"
        INVALID_FIELD_ERROR_MESSAGE = f"Invalid {field_type} '{field}' having value {self._wrap_in_quotes_if_string(field_value)}"
        self._register_validated_data(field=field, field_value=field_value)
        if field_validator_instance.can_be_set_to_null():
            return
        if is_empty(field_value) and required:
            self._unregister_validated_data(field=field)
            self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'message': MISSING_FIELD_ERROR_MESSAGE})
            self._register_error(error_kwargs=error_kwargs)
            self._raise_exception_if_needed(error_kwargs=error_kwargs, raise_exception=raise_exception)
            return
        if is_empty(field_value) and not required:
            self._unregister_validated_data(field=field)
            return
        field_validator_instance.field_value = field_value
        if not field_validator_instance.is_valid():
            self._unregister_validated_data(field=field)
            self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'message': INVALID_FIELD_ERROR_MESSAGE})
            self._register_error(error_kwargs=error_kwargs)
            self._raise_exception_if_needed(error_kwargs=error_kwargs, raise_exception=raise_exception)
            return
        if not field_validator_instance.custom_validators_are_valid():
            self._unregister_validated_data(field=field)
            self._update_error_kwargs(error_kwargs=error_kwargs, kwarg={'message': INVALID_FIELD_ERROR_MESSAGE})
            self._register_error(error_kwargs=error_kwargs)
            self._raise_exception_if_needed(error_kwargs=error_kwargs, raise_exception=raise_exception)
            return
        return None

    def _perform_class_validation_checks(
            self,
            *,
            class_validator: Callable,
            raise_exception: bool,
        ) -> None:
        """Performs validation checks for the given Meta class, and registers/raises errors (if any)"""
        error_kwargs = class_validator(values=self._validated_data.copy())
        assert (error_kwargs is None or isinstance(error_kwargs, dict)), (
            "Output of Meta class validator functions should be either NoneType or dictionary having error kwargs"
        )
        if error_kwargs is None:
            return None
        self._register_error(error_kwargs=error_kwargs)
        self._raise_exception_if_needed(error_kwargs=error_kwargs, raise_exception=raise_exception)
        return None

    def is_valid(self, *, raise_exception: Optional[bool] = False) -> bool:
        """Returns boolean. If `raise_exception=True` and data validation fails, then raises `ValidationError`"""
        assert isinstance(self.data, dict), "Cannot call `is_valid()` without setting the `data` dictionary"
        for field, field_validator_instance in self._field_validators_dict.items():
            self._perform_field_validation_checks(
                field=field,
                field_validator_instance=field_validator_instance,
                raise_exception=raise_exception,
            )
        if not self.errors:  # perform class validator checks ONLY IF there are no errors in field validator checks
            for class_validator in self._class_validators:
                self._perform_class_validation_checks(
                    class_validator=class_validator,
                    raise_exception=raise_exception,
                )
        return False if self.errors else True

