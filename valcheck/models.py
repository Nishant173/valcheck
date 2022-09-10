from typing import Any, Dict, Optional


class Error:
    """Class that represents an error"""

    def __init__(
            self,
            *,
            details: Optional[Any] = None,
            source: Optional[str] = None,
            code: Optional[str] = None,
        ) -> None:
        assert (source is None or isinstance(source, str)), "Param `source` must be a string"
        assert (code is None or isinstance(code, str)), "Param `code` must be a string"
        self.details = details
        self.source = source or ""
        self.code = code or ""
        self._validator_message = ""

    @property
    def validator_message(self) -> str:
        return self._validator_message

    @validator_message.setter
    def validator_message(self, value: str) -> None:
        self._validator_message = value

    def as_dict(self) -> Dict[str, Any]:
        return {
            "details": self.details,
            "source": self.source,
            "code": self.code,
            "validator_message": self.validator_message,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

