from typing import List, Optional

from valcheck.apis import status_codes
from valcheck.apis.exceptions import ApiException
from valcheck.models import Error
from valcheck.validators import Validator


class ApiRequestValidator(Validator):

    HTTP_STATUS_CODE: int = status_codes.HTTP_418_IM_A_TEAPOT

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> List[Error]:
        """
        Runs validations and registers errors/validated-data. Returns list of errors.
        If `raise_exception=True` and validations fail, raises `valcheck.apis.exceptions.ApiException`.
        """
        errors = super().run_validations(raise_exception=False)
        if raise_exception and errors:
            raise ApiException(
                http_status_code=self.HTTP_STATUS_CODE,
                errors=errors,
            )
        return errors

