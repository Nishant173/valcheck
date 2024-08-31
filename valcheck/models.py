from __future__ import annotations

from typing import Any, Dict, Optional

from valcheck import utils


class Error:
    """Class that represents an error"""

    def __init__(
            self,
            *,
            description: Optional[str] = None,
            code: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
            initial_field_path: Optional[str] = None,
        ) -> None:
        assert (description is None or isinstance(description, str)), "Param `description` must be a string"
        assert (code is None or isinstance(code, str)), "Param `code` must be a string"
        assert (details is None or isinstance(details, dict)), "Param `details` must be a dictionary"
        assert (initial_field_path is None or isinstance(initial_field_path, str)), "Param `initial_field_path` must be a string"
        self.description = description or ""
        self.code = code or ""
        self.details = details or {}
        self._validator_message = ""
        self._field_path = initial_field_path or ""

    def copy(self) -> Error:
        """Returns deep-copy of current `Error` object"""
        return utils.make_deep_copy(self)

    @property
    def validator_message(self) -> str:
        return self._validator_message

    @validator_message.setter
    def validator_message(self, value: str) -> None:
        assert isinstance(value, str), "The param `validator_message` must be a string"
        self._validator_message = value

    @property
    def field_path(self) -> str:
        return self._field_path

    @field_path.setter
    def field_path(self, value: str) -> None:
        assert isinstance(value, str), "The param `field_path` must be a string"
        self._field_path = value

    def append_to_field_path(
            self,
            s: str,
            /,
            *,
            at_beginning: Optional[bool] = True,
            separator: Optional[str] = " --> ",
        ) -> None:
        """Appends the given string `s` to the `field_path` (in-place)"""
        if not self.field_path:
            self.field_path += s
            return
        self.field_path = (
            s + separator + self.field_path
            if at_beginning else
            self.field_path + separator + s
        )

    def as_dict(
            self,
            *,
            include_validator_message: Optional[bool] = True,
            include_field_path: Optional[bool] = True,
        ) -> Dict[str, Any]:
        dict_ = {
            "description": self.description,
            "code": self.code,
            "details": self.details,
        }
        if include_validator_message:
            dict_["validator_message"] = self.validator_message
        if include_field_path:
            dict_["field_path"] = self.field_path
        return dict_

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.as_dict()})"

