from typing import Any

from valcheck.exceptions import ValidationException


class ApiException(ValidationException):
    """Exception to be raised when an API error occurs"""

    def __init__(self, *, http_status_code: int, **kwargs: Any) -> None:
        self._http_status_code = http_status_code
        super(ApiException, self).__init__(**kwargs)

    @property
    def http_status_code(self) -> int:
        return self._http_status_code

    @http_status_code.setter
    def http_status_code(self, value: int) -> None:
        assert isinstance(value, int), "Param `http_status_code` must be an integer"
        self._http_status_code = value

