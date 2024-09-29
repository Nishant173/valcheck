import functools
from typing import Any, Callable, Dict, Optional, Type

from valcheck.exceptions import FunctionInputValidationException
from valcheck.utils import dicts_have_common_keys
from valcheck.validators import Validator


def function_input_validator(
        *,
        validator_model: Type[Validator],
        validator_model_kwargs: Optional[Dict[str, Any]] = None,
        args_to_kwargs: Optional[Callable[(...), Dict[str, Any]]] = None,
    ) -> Callable:
    """
    Decorator that validates the input parameters of the decorated function.
    If validation of function input fails, raises `valcheck.exceptions.FunctionInputValidationException`.

    Parameters:
        - validator_model (Type[Validator]): The validator model used to perform the validation.
        - validator_model_kwargs (dict): Parameters to `validator_model` (if any). The `data` parameter will already be plugged in.
        - args_to_kwargs (Callable): Callable that takes in the args (positional arguments if any) of the decorated function, and returns
        the corresponding kwargs (keyword arguments) as a dictionary. This is necessary since `validator_model` only accepts kwargs.
    """

    assert validator_model is not Validator and issubclass(validator_model, Validator), (
        "Param `validator_model` must be a sub-class of `valcheck.validators.Validator`"
    )
    assert validator_model_kwargs is None or isinstance(validator_model_kwargs, dict), "Param `validator_model_kwargs` must be a dictionary"
    assert args_to_kwargs is None or callable(args_to_kwargs), "Param `args_to_kwargs` must be a callable"

    validator_model_kwargs = validator_model_kwargs or {}

    def outer_func(func: Callable) -> Callable:
        @functools.wraps(func)
        def inner_func(*args: Any, **kwargs: Any) -> Any:
            args_as_kwargs = args_to_kwargs(*args) if args_to_kwargs else {}
            assert isinstance(args_as_kwargs, dict), "Param `args_to_kwargs` must return a dictionary"
            assert not dicts_have_common_keys(args_as_kwargs, kwargs), (
                "The output of `args_to_kwargs` must have keys that are distinct compared to the keys of the decorated function's input kwargs"
            )
            data = {
                **args_as_kwargs,
                **kwargs,
            }
            val = validator_model(data=data, **validator_model_kwargs)
            val.run_validations()
            if val.errors:
                raise FunctionInputValidationException(errors=val.errors)
            result = func(*args, **kwargs)
            return result
        return inner_func
    return outer_func

