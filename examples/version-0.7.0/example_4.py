## Writing a validator with an advanced field i.e; `valcheck.fields.ModelListField`

from datetime import datetime
from pprint import pprint

from valcheck import fields, models, validator


ITEM_NAMES = ("Apple", "Banana", "Lemon", "Orange")
ITEM_UNITS = ("kgs", "grams")


class ItemValidator(validator.Validator):
    name = fields.ChoiceField(
        choices=ITEM_NAMES,
        error=models.Error(details={"message": f"Item name must be one of {'|'.join(ITEM_NAMES)}"}),
    )
    quantity = fields.NumberField(
        validators=[lambda qty: qty > 0],
        error=models.Error(details={"message": "Item quantity must be a number > 0"}),
    )
    unit = fields.ChoiceField(
        choices=ITEM_UNITS,
        error=models.Error(details={"message": f"Item unit (of measurement) must be one of {'|'.join(ITEM_UNITS)}"}),
    )


class CartValidator(validator.Validator):
    timestamp_of_purchase = fields.DatetimeStringField(
        format_="%Y-%m-%d %H:%M:%S",
        converter_factory=lambda ts_string: datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S"),
    )
    items = fields.ModelListField(validator_model=ItemValidator, allow_empty=False)


if __name__ == "__main__":
    data = {
        "timestamp_of_purchase": "2023-02-18 17:45:30",
        "items": [
            {
                "name": "Banana",
                "quantity": 1.5,
                "unit": "kgs",
            },
            {
                "name": "Orange",
                "quantity": 200,
                "unit": "grams",
            },
            {
                "name": "Apple",
                "quantity": 800,
                "unit": "grams",
            },
        ],
    }
    cart_validator = CartValidator(data=data)
    errors = cart_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(cart_validator.validated_data) # Dictionary having validated data (by field)
