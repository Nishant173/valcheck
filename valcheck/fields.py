from typing import Any, Callable, Dict, Iterable, List, Optional

from valcheck.utils import (
    is_instance_of_any,
    is_iterable,
    is_valid_datetime_string,
    is_valid_email_id,
    is_valid_uuid_string,
    set_as_empty,
)


class BaseField:
    def __init__(
            self,
            *,
            required: Optional[bool] = True,
            nullable: Optional[bool] = False,
            validators: Optional[List[Callable]] = None,
            error_kwargs: Optional[Dict[str, Any]] = None,
        ) -> None:
        assert isinstance(required, bool), "Param `required` must be of type 'bool'"
        assert isinstance(nullable, bool), "Param `nullable` must be of type 'bool'"
        assert validators is None or isinstance(validators, list), "Param `validators` must be of type 'list'"
        if isinstance(validators, list):
            for validator in validators:
                assert callable(validator), "Param `validators` must be a list of callables"
        assert error_kwargs is None or isinstance(error_kwargs, dict), "Param `error_kwargs` must be of type 'dict'"

        self._field_value = set_as_empty()
        self.required = required
        self.nullable = nullable
        self.validators = validators or []
        self.error_kwargs = error_kwargs or {}

    @property
    def field_value(self) -> Any:
        return self._field_value

    @field_value.setter
    def field_value(self, value: Any) -> None:
        self._field_value = value

    def can_be_set_to_null(self) -> bool:
        return self.nullable and self.field_value is None

    def custom_validators_are_valid(self) -> bool:
        if not self.validators:
            return True
        validator_return_values = [validator(self.field_value) for validator in self.validators]
        for return_value in validator_return_values:
            assert isinstance(return_value, bool), (
                f"Expected the return type of `validators` to be 'bool', but got '{type(return_value).__name__}'"
            )
        return all(validator_return_values)

    def is_valid(self) -> bool:
        raise NotImplementedError()


class BooleanField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(BooleanField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, bool)


class StringField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(StringField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, str)


class EmailIdField(StringField):
    def __init__(self, **kwargs: Any) -> None:
        super(EmailIdField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and is_valid_email_id(self.field_value)
        )


class UuidStringField(StringField):
    def __init__(self, **kwargs: Any) -> None:
        super(UuidStringField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and is_valid_uuid_string(self.field_value)
        )


class DateStringField(StringField):
    def __init__(self, format_: Optional[str] = "%Y-%m-%d", **kwargs: Any) -> None:
        self.format_ = format_
        super(DateStringField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and is_valid_datetime_string(self.field_value, self.format_)
        )


class DatetimeStringField(StringField):
    def __init__(self, format_: Optional[str] = "%Y-%m-%d %H:%M:%S", **kwargs: Any) -> None:
        self.format_ = format_
        super(DatetimeStringField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and is_valid_datetime_string(self.field_value, self.format_)
        )


class ChoiceField(BaseField):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(ChoiceField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return self.field_value in self.choices


class IntegerField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(IntegerField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, int)


class PositiveIntegerField(IntegerField):
    def __init__(self, **kwargs: Any) -> None:
        super(PositiveIntegerField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and self.field_value > 0
        )


class NegativeIntegerField(IntegerField):
    def __init__(self, **kwargs: Any) -> None:
        super(NegativeIntegerField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and self.field_value < 0
        )


class FloatField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(FloatField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, float)


class NumberField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(NumberField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return is_instance_of_any(obj=self.field_value, types=[int, float])


class DictionaryField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(DictionaryField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, dict)


class ListField(BaseField):
    def __init__(self, **kwargs: Any) -> None:
        super(ListField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return isinstance(self.field_value, list)


class MultiChoiceField(ListField):
    def __init__(self, *, choices: Iterable[Any], **kwargs: Any) -> None:
        assert is_iterable(choices), "Param `choices` must be an iterable"
        self.choices = choices
        super(MultiChoiceField, self).__init__(**kwargs)

    def is_valid(self) -> bool:
        if super().can_be_set_to_null():
            return True
        return (
            super().is_valid()
            and all([item in self.choices for item in self.field_value])
        )

