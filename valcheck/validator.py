from typing import Any, Dict, List, Optional, Union

from valcheck.exceptions import MissingFieldException, ValidationException
from valcheck.fields import Field
from valcheck.models import Error
from valcheck.utils import Empty, is_empty, is_list_of_instances_of_type, set_as_empty


class Validator:
    """
    Properties:
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
        self._field_info: Dict[str, Field] = self._initialise_fields()
        self._errors: List[Error] = []
        self._validated_data: Dict[str, Any] = {}

    def list_field_validators(self) -> List[Dict[str, Any]]:
        return [
            {
                "field_type": field.__class__.__name__,
                "field_identifier": field_identifier,
                "field_name": field.field_name,
                "alias": field.alias,
                "required": field.required,
                "nullable": field.nullable,
            } for field_identifier, field in self._field_info.items()
        ]

    def _initialise_fields(self) -> Dict[str, Field]:
        """Returns dictionary having keys = field identifiers, and values = initialised field instances"""
        field_info = {}
        vars_dict = vars(self.__class__)
        for field_identifier in vars_dict:
            field: Field = vars_dict[field_identifier]
            if (
                not field_identifier.startswith("__")
                and isinstance(field_identifier, str)
                and field.__class__ is not Field
                and issubclass(field.__class__, Field)
            ):
                field.field_identifier = field_identifier
                field.field_name = field.alias if field.alias else field_identifier
                field.field_value = self.data.get(field.field_name, set_as_empty())
                field_info[field_identifier] = field
        return field_info

    def _clear_errors(self) -> None:
        """Clears out the list of errors"""
        self._errors.clear()

    def _register_errors(self, *, errors: List[Error]) -> None:
        self._errors.extend(errors)

    def _register_validated_data(self, *, key: str, value: Any) -> None:
        self._validated_data[key] = value

    @property
    def validated_data(self) -> Dict[str, Any]:
        return self._validated_data

    def _clear_validated_data(self) -> None:
        """Clears out the dictionary having validated data"""
        self._validated_data.clear()

    def get_field_value(self, field: str, default: Union[Any, Empty] = set_as_empty(), /) -> Any:
        """
        Returns the validated field value. Raises `valcheck.exceptions.MissingFieldException` if the field
        is missing, and no default is provided.
        """
        if field in self.validated_data:
            return self.validated_data[field]
        if not is_empty(default):
            return default
        raise MissingFieldException(f"The field '{field}' is missing from the validated data")

    def _perform_field_validation_checks(self, *, field: Field) -> None:
        """Performs validation checks for the given field, and registers errors (if any) and validated-data"""
        validated_field = field.run_validations()
        if validated_field.errors:
            self._register_errors(errors=validated_field.errors)
            return
        if not is_empty(validated_field.field_value):
            self._register_validated_data(key=validated_field.field_identifier, value=validated_field.field_value)

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
        Used to validate the entire model, after all individual fields are validated.
        The output of the model validator method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        return []

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> List[Error]:
        """
        Runs validations and registers errors/validated-data. Returns list of errors.
        If `raise_exception=True` and validations fail, raises `valcheck.exceptions.ValidationException`.
        """
        self._clear_errors()
        self._clear_validated_data()
        for _, field in self._field_info.items():
            self._perform_field_validation_checks(field=field)
        # Perform model validation checks only if there are no errors in field validation checks
        if not self._errors:
            self._perform_model_validation_checks()
        if self._errors:
            self._clear_validated_data()
        if raise_exception and self._errors:
            raise ValidationException(errors=self._errors)
        return self._errors

