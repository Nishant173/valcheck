from typing import Any, Dict, Optional


class ValidationError(Exception):
    """Exception to be raised when data validation fails"""

    def __init__(
            self,
            *,
            details: Optional[Any] = None,
            source: Optional[str] = None,
            code: Optional[str] = None,
            validator_message: Optional[str] = None,
        ) -> None:
        assert (source is None or isinstance(source, str)), "Param `source` must be a string"
        assert (code is None or isinstance(code, str)), "Param `code` must be a string"
        assert (validator_message is None or isinstance(validator_message, str)), "Param `validator_message` must be a string"
        self.details = details
        self.source = source or ""
        self.code = code or ""
        self.validator_message = validator_message or ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "details": self.details,
            "source": self.source,
            "code": self.code,
            "validator_message": self.validator_message,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

