from typing import Any, Dict

from valcheck.exceptions import BaseValidationException


class ApiRequestValidationException(BaseValidationException):
    """Exception to be raised when an API error occurs"""

    def __init__(self, *, http_status_code: int, **kwargs: Any) -> None:
        assert isinstance(http_status_code, int), "Param `http_status_code` must be an integer"
        self._http_status_code = http_status_code
        super(ApiRequestValidationException, self).__init__(**kwargs)

    @property
    def http_status_code(self) -> int:
        return self._http_status_code

    @http_status_code.setter
    def http_status_code(self, value: int) -> None:
        assert isinstance(value, int), "Param `http_status_code` must be an integer"
        self._http_status_code = value

    def as_dict(self) -> Dict[str, Any]:
        dict_obj = super().as_dict()
        dict_obj["http_status_code"] = self.http_status_code
        return dict_obj

