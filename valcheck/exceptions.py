from typing import Any, Dict, List

from valcheck.models import Error
from valcheck.utils import is_list_of_instances_of_type


def _validate_list_of_errors(obj: Any, /) -> None:
    """Ensures that the given object is a list of errors (each of type `valcheck.models.Error`)"""
    if not is_list_of_instances_of_type(obj, type_=Error, allow_empty=True):
        raise ValueError("Must be list of errors (each of type `valcheck.models.Error`)")


class InvalidFieldIdentifierException(Exception):
    """Exception to be raised when a validator finds an invalid field-identifier for it's fields"""
    pass


class DuplicateSourcesException(Exception):
    """Exception to be raised when a validator finds duplicate sources for it's fields"""
    pass


class DuplicateTargetsException(Exception):
    """Exception to be raised when a validator finds duplicate targets for it's fields"""
    pass


class MissingFieldException(Exception):
    """Exception to be raised when a field is missing"""
    pass


class BaseValidationException(Exception):
    """Base class for all validation failure exceptions"""

    def __init__(self, *, errors: List[Error]) -> None:
        _validate_list_of_errors(errors)
        self._errors = errors

    @property
    def errors(self) -> List[Error]:
        return self._errors

    @errors.setter
    def errors(self, value: List[Error]) -> None:
        _validate_list_of_errors(value)
        self._errors = value

    def as_dict(self) -> Dict[str, Any]:
        return {
            "errors": [error.as_dict() for error in self.errors],
            "error_count": len(self.errors),
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"


class ValidationException(BaseValidationException):
    """Exception to be raised when data validation fails"""

    def __init__(self, **kwargs: Any) -> None:
        super(ValidationException, self).__init__(**kwargs)


class FunctionInputValidationException(BaseValidationException):
    """Exception to be raised when data validation fails for a function's input parameters"""

    def __init__(self, **kwargs: Any) -> None:
        super(FunctionInputValidationException, self).__init__(**kwargs)


