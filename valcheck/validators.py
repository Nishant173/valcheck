from __future__ import annotations

import string
from typing import Any, Callable, Dict, List, Optional, Type, Union

from valcheck.exceptions import (
    DuplicateSourcesException,
    DuplicateTargetsException,
    InvalidFieldIdentifierException,
    MissingFieldException,
    ValidationException,
)
from valcheck.fields import Field, ModelDictionaryField, ModelListField
from valcheck.models import Error
from valcheck import utils


class Validator:
    """
    Properties:
        - context
        - data
        - errors
        - extra_data
        - validated_data

    Instance methods:
        - get_representation()
        - get_validated_value()
        - list_field_validators()
        - model_validator()
        - model_validators_to_consider()
        - run_validations()
    """

    def __init__(
            self,
            *,
            data: Dict[str, Any],
            context: Optional[Dict[str, Any]] = None,
            deep_copy: Optional[bool] = False,
        ) -> None:
        assert isinstance(data, dict), "Param `data` must be a dictionary"
        assert context is None or isinstance(context, dict), "Param `context` must be a dictionary"
        context = context if context else {}
        self._data: Dict[str, Any] = utils.make_deep_copy(data) if deep_copy else data
        self._context: Dict[str, Any] = utils.make_deep_copy(context) if deep_copy else context
        self._field_info: Dict[str, Field] = self._initialise_fields()
        self._errors: List[Error] = []
        self._validated_data: Dict[str, Any] = {}

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    @property
    def context(self) -> Dict[str, Any]:
        return self._context

    def list_field_validators(self) -> List[Dict[str, Any]]:
        """Returns list of all the registered field validators"""
        return [
            {
                "field_type": field.__class__.__name__,
                "field_identifier": field_identifier,
                "source": field.source,
                "target": field.target,
                "required": field.required,
                "nullable": field.nullable,
                "field_validators_of_model": (
                    field.validator_model(data={}).list_field_validators()
                    if utils.is_instance_of_any(obj=field, types=[ModelDictionaryField, ModelListField])
                    else []
                ),
            } for field_identifier, field in self._field_info.items()
        ]

    def _get_field_key_picker(self, *, key: str) -> Callable[[Field], str]:
        """
        Validates the `key` and returns a callable.
        The callable takes in a field and returns the field's attribute based on `key`.
        """
        key_mapper = {
            "field_identifier": lambda field_obj: field_obj.field_identifier,
            "source": lambda field_obj: field_obj.source,
            "target": lambda field_obj: field_obj.target,
        }
        assert key in key_mapper, f"Param `key` must be one of {list(key_mapper.keys())}"
        return key_mapper[key]

    def get_representation(self, *, key: str) -> Dict[str, Any]:
        """
        Returns dictionary having the representation of the expected data format.
        Options for `key` are: `['field_identifier', 'source', 'target']`.
        """
        field_key_picker = self._get_field_key_picker(key=key)
        representation = {}
        for _, field in self._field_info.items():
            field_key = field_key_picker(field)
            if isinstance(field, ModelDictionaryField):
                representation[field_key] = field.sample_value(key=key)
            elif isinstance(field, ModelListField):
                representation[field_key] = field.sample_value(key=key)
            else:
                representation[field_key] = field.sample_value()
        return representation

    def _validate_field_identifier(self, field_identifier: str, /) -> None:
        """If an invalid field-identifier is found, raises `valcheck.exceptions.InvalidFieldIdentifierException`"""
        error_message = (
            f"Invalid field identifier '{field_identifier}'."
            " The first character must be a lowercase alphabet."
            " Can only contain lowercase alphabets, numbers, and underscores."
        )
        if not (
            isinstance(field_identifier, str)
            and bool(field_identifier)
        ):
            raise InvalidFieldIdentifierException(error_message)
        allowed_chars = string.ascii_lowercase + string.digits + '_'
        for idx, char in enumerate(field_identifier):
            if idx == 0 and char not in string.ascii_lowercase:
                raise InvalidFieldIdentifierException(error_message)
            if char not in allowed_chars:
                raise InvalidFieldIdentifierException(error_message)

    def _validate_uniqueness_of_sources_and_targets(self, field_info: Dict[str, Field], /) -> None:
        """
        If duplicate sources/targets are found, raises `valcheck.exceptions.DuplicateSourcesException`
        or `valcheck.exceptions.DuplicateTargetsException`
        """
        sources, targets = [], []
        for _, field in field_info.items():
            if field.source:
                sources.append(field.source)
            if field.target:
                targets.append(field.target)
        if len(sources) != len(set(sources)):
            raise DuplicateSourcesException(f"Received duplicate values for `source`: {sorted(sources)}")
        if len(targets) != len(set(targets)):
            raise DuplicateTargetsException(f"Received duplicate values for `target`: {sorted(targets)}")

    def _initialise_fields(self) -> Dict[str, Field]:
        """Returns dictionary having keys = field identifiers, and values = initialised field instances"""
        vars_dict: Dict[str, Any] = {}
        for class_ in reversed(self.__class__.__mro__):
            vars_dict.update(**vars(class_))
        field_info = {}
        for field_identifier in vars_dict:
            temp_field: Field = vars_dict[field_identifier]
            if (
                isinstance(field_identifier, str)
                and temp_field.__class__ is not Field
                and issubclass(temp_field.__class__, Field)
            ):
                self._validate_field_identifier(field_identifier)
                field = temp_field.copy()
                field.field_identifier = field_identifier
                field.source = field.source if field.source else field_identifier
                field.target = field.target if field.target else field_identifier
                field.field_value = self.data.get(field.source, utils.set_as_empty())
                field_info[field_identifier] = field
        self._validate_uniqueness_of_sources_and_targets(field_info)
        return field_info

    @property
    def errors(self) -> List[Error]:
        return self._errors

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

    @property
    def extra_data(self) -> Dict[str, Any]:
        """
        Returns dictionary containing the extra data (key-value pairs) which is present in the `data` dictionary, but not a part of
        the fields being validated by the validator.
        """
        sources = set(
            filter(
                None,
                (
                    field_instance.source if field_instance.source else None for _, field_instance in self._field_info.items()
                ),
            )
        )
        extra_keys_in_data = set(self.data.keys()).difference(sources)
        return { key : value for key, value in self.data.items() if key in extra_keys_in_data }

    def get_validated_value(
            self,
            field_target: str,
            default: Union[Any, utils.Empty] = utils.set_as_empty(),
            /,
        ) -> Any:
        """
        Returns the validated field value. Raises `valcheck.exceptions.MissingFieldException` if the field
        is missing, and no default is provided.
        """
        if field_target in self.validated_data:
            return self.validated_data[field_target]
        if not utils.is_empty(default):
            return default
        raise MissingFieldException(f"The field target '{field_target}' is missing from the validated data")

    def _perform_field_validation_checks(self, *, field: Field) -> None:
        """Performs validation checks for the given field, and registers errors (if any) and validated-data"""
        validated_field = field.validate_entire_field()
        if validated_field.errors:
            self._register_errors(errors=validated_field.errors)
            return
        if not utils.is_empty(validated_field.field.field_value):
            self._register_validated_data(
                key=validated_field.field.target,
                value=validated_field.field.field_value,
            )

    def _perform_model_validation_checks(self) -> None:
        """Performs model validation checks, and registers errors (if any)"""
        errors: List[Error] = []
        model_validator_classes_to_consider = self.model_validators_to_consider()
        assert utils.is_list_of_subclasses_of_type(
            model_validator_classes_to_consider,
            type_=Validator,
            allow_empty=True,
        ), (
            "The output of the `model_validators_to_consider()` method must be a list of types, each"
            " being a sub-class of `valcheck.validators.Validator`."
            " Must be an empty list if there are no parent classes to consider."
        )
        if self.__class__ not in model_validator_classes_to_consider:
            model_validator_classes_to_consider += [self.__class__]
        for class_ in self.__class__.__mro__:
            if (
                class_ is not Validator
                and issubclass(class_, Validator)
                and class_ in model_validator_classes_to_consider
                and "model_validator" in class_.__dict__  # the `model_validator()` method must be implemented in said class
            ):
                errors += class_.model_validator(self)
        assert utils.is_list_of_instances_of_type(errors, type_=Error, allow_empty=True), (
            "The output of the `model_validator()` method must be a list of errors (each of type `valcheck.models.Error`)."
            " Must be an empty list if there are no errors."
        )
        INVALID_MODEL_ERROR_MESSAGE = "Invalid model - Validation failed"
        for error in errors:
            error.validator_message = INVALID_MODEL_ERROR_MESSAGE
        self._register_errors(errors=errors)

    def model_validators_to_consider(self) -> List[Type[Validator]]:
        """
        Used to determine which classes in the hierarchy need to be considered while calling the `model_validator()` method.
        The output of this method must be a list of class references of type `valcheck.validators.Validator`.
        Must be an empty list if there are no parent classes to consider.
        """
        return []

    def model_validator(self) -> List[Error]:
        """
        Used to validate the entire model, after all individual fields are validated.
        The output of this method must be a list of errors (each of type `valcheck.models.Error`).
        Must be an empty list if there are no errors.
        """
        return []

    def run_validations(self, *, raise_exception: Optional[bool] = False) -> None:
        """
        Runs validations and registers errors/validated-data.
        If `raise_exception=True` and validations fail, raises `valcheck.exceptions.ValidationException`.
        """
        self._clear_errors()
        self._clear_validated_data()
        for _, field in self._field_info.items():
            self._perform_field_validation_checks(field=field)
        # Perform model validation checks only if there are no errors in field validation checks
        if not self.errors:
            self._perform_model_validation_checks()
        if self.errors:
            self._clear_validated_data()
        if raise_exception and self.errors:
            raise ValidationException(errors=self.errors)
