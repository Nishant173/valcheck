from typing import Any, Dict, Optional


class ValidationError(Exception):
    """Exception to be raised when data validation fails"""

    def __init__(
            self,
            *,
            message: Optional[str] = None,
            source: Optional[str] = None,
            code: Optional[str] = None,
            details: Optional[Any] = None,
        ) -> None:
        self.message = message or ""
        self.source = source or ""
        self.code = code or ""
        self.details = details

    def as_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "source": self.source,
            "code": self.code,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

