from typing import Any, Dict, List, Optional

from valcheck.exceptions import MissingFieldException, ValidationException
from valcheck.fields import Field
from valcheck.models import Error
from valcheck.utils import is_empty, is_list_of_instances_of_type, set_as_empty


class Validator:
    """
    Properties:
        - converted_data
        - validated_data

    Instance methods:
        - get_field_value()
        - list_field_validators()
        - model_validator()
        - run_validations()
    """

    def __init__(self, *, data: Dict[str, Any]) -> None:
        assert isinstance(data, dict), "Param `data` must be a dictionary"
        self.data = data
        self._field_validators_dict: Dict[str, Field] = self._get_field_validators_dict()
        self._errors: List[Error] = []
        self._validated_data: Dict[str, Any] = {}
        self._converted_data: Dict[str, Any] = {}

    def list_field_validators(self) -> List[Dict[str, Any]]:
        return [
            {
                "field_type": field.__class__.__name__,
                "field_name": field_name,
            } for field_name, field in self._field_validators_dict.items()
        ]

    def _get_field_validators_dict(self) -> Dict[str, Field]:
        """Returns dictionary having keys = field names, and values = field validator instances"""
        return {
            field_name : field_validator_instance for field_name, field_validator_instance in vars(self.__class__).items() if (
                not field_name.startswith("__")
                and isinstance(field_name, str)
                and field_validator_instance.__class__ is not Field
                and issubclass(field_validator_instance.__class__, Field)
            )
        }

    def _clear_errors(self) -> None:
        """Clears out the list of errors"""
        self._errors.clear()

    def _register_errors(self, *, errors: List[Error]) -> None:
        self._errors.extend(errors)

    def _register_validated_data(self, *, field_name: str, field_value: Any) -> None:
        self._validated_data[field_name] = field_value

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def _clear_validated_data(self) -> None:
        """Clears out the dictionary having validated data"""
        self._validated_data.clear()

    def _register_converted_data(self, *, field_name: str, value: Any) -> None:
        self._converted_data[field_name] = value

    def _clear_converted_data(self) -> None:
        """Clears out the dictionary having converted data"""
        self._converted_data.clear()

    @property
    def converted_data(self) -> Dict[str, Any]:
        return self._converted_data

    def get_field_value(self, field: str, /) -> Any:
        """Returns the validated field value. Raises `valcheck.exceptions.MissingFieldException` if the field is missing"""
        if field in self.validated_data:
            return self.validated_data[field]
        raise MissingFieldException(f"The field '{field}' is missing from the validated data")

    def _perform_field_validation_checks(self, *, field: Field) -> None:
        """Performs validation checks for the given field, and registers errors (if any) and validated data"""
        field_info = field.run_validations()
        if field_info.errors:
            self._register_errors(errors=field_info.errors)
            return
        self._register_validated_data(field_name=field_info.field_name, field_value=field_info.field_value)
        self._register_converted_data(
            field_name=field_info.field_name,
            value=field_info.field_value if is_empty(field_info.converted_value) else field_info.converted_value,
        )

    def _perform_model_validation_checks(self) -> None:
        """Performs model validation checks, and registers errors (if any)"""
        errors = self.model_validator()
        assert is_list_of_instances_of_type(errors, type_=Error, allow_empty=True), (
            "The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`)."
            " Must be an empty list if there are no errors."
        )
        INVALID_MODEL_ERROR_MESSAGE = "Invalid model - Validation failed"
        for error in errors:
            error.validator_message = INVALID_MODEL_ERROR_MESSAGE
        self._register_errors(errors=errors)

    def model_validator(self) -> List[Error]:
        """
        The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        return []

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> List[Error]:
        """
        Runs validations and registers errors / validated data. Returns list of errors.
        If `raise_exception=True` and validations fail, raises `valcheck.exceptions.ValidationException`.
        """
        self._clear_errors()
        self._clear_validated_data()
        for field_name, field in self._field_validators_dict.items():
            field.field_name = field_name
            field.field_value = self.data.get(field_name, set_as_empty())
            self._perform_field_validation_checks(field=field)
        # Perform model validation checks only if there are no errors in field validation checks
        if not self._errors:
            self._perform_model_validation_checks()
        if self._errors:
            self._clear_validated_data()
            self._clear_converted_data()
        if raise_exception and self._errors:
            raise ValidationException(errors=self._errors)
        return self._errors

