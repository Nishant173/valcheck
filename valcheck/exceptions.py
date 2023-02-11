from typing import Any, Dict, List

from valcheck.models import Error


def _validate_list_of_errors(obj: Any, /) -> None:
    """Ensures that the given object is a list of errors; each of type `valcheck.models.Error`"""
    assert isinstance(obj, list), "Must be list of errors"
    for error in obj:
        assert isinstance(error, Error), "Must be list of errors; each of type `valcheck.models.Error`"


class MissingFieldException(Exception):
    """Exception to be raised when a field is missing"""
    pass


class ValidationException(Exception):
    """Exception to be raised when data validation fails"""

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
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

