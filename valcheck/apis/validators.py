from typing import Optional

from valcheck.apis import status_codes
from valcheck.apis.exceptions import ApiRequestValidationException
from valcheck.validators import Validator


class ApiRequestValidator(Validator):
    """Class that represents an API request Validator."""

    HTTP_STATUS_CODE: int = status_codes.HTTP_418_IM_A_TEAPOT

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> None:
        """
        Runs validations and registers errors/validated-data.
        If `raise_exception=True` and validations fail, raises `valcheck.apis.exceptions.ApiRequestValidationException`.
        """
        super().run_validations()
        if raise_exception and self.errors:
            raise ApiRequestValidationException(
                http_status_code=self.HTTP_STATUS_CODE,
                errors=self.errors,
            )

