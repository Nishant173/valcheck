from typing import Any, Dict


class ValidationError(Exception):
    """Exception to be raised when data validation fails"""

    def __init__(self, *, error_info: Any) -> None:
        self.error_info = error_info

    def as_dict(self) -> Dict[str, Any]:
        return {
            "error_info": self.error_info,
        }

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

