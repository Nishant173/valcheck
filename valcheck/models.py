from typing import Any, Dict, Optional


class Error:
    """Class that represents an error"""

    def __init__(
            self,
            *,
            description: Optional[str] = None,
            code: Optional[str] = None,
            source: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
        ) -> None:
        assert (description is None or isinstance(description, str)), "Param `description` must be a string"
        assert (code is None or isinstance(code, str)), "Param `code` must be a string"
        assert (source is None or isinstance(source, str)), "Param `source` must be a string"
        assert (details is None or isinstance(details, dict)), "Param `details` must be a dictionary"
        self.description = description or ""
        self.code = code or ""
        self.source = source or ""
        self.details = details or {}
        self._validator_message = ""

    @property
    def validator_message(self) -> str:
        return self._validator_message

    @validator_message.setter
    def validator_message(self, value: str) -> None:
        assert isinstance(value, str), "The param `validator_message` must be a string"
        self._validator_message = value

    def as_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "code": self.code,
            "source": self.source,
            "details": self.details,
            "validator_message": self.validator_message,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

