from typing import Any, Optional

from valcheck.apis import status_codes
from valcheck.apis.exceptions import ApiRequestValidationException
from valcheck.validators import Validator


class ApiRequestValidator(Validator):
    """Class that represents an API request Validator."""

    def run_validations(self, *, raise_exception: Optional[bool] = False, **kwargs: Any) -> None:
        """
        Runs validations and registers errors/validated-data.
        If `raise_exception=True` and validations fail, raises `valcheck.apis.exceptions.ApiRequestValidationException`.

        Accepted kwargs:
            - http_status_code (int): The HTTP status code to use if `valcheck.apis.exceptions.ApiRequestValidationException` is raised. Default: 418.
        """
        super().run_validations()
        if raise_exception and self.errors:
            http_status_code: int = kwargs.get("http_status_code", status_codes.HTTP_418_IM_A_TEAPOT)
            raise ApiRequestValidationException(
                http_status_code=http_status_code,
                errors=self.errors,
            )

