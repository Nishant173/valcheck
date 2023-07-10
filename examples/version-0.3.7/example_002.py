from datetime import datetime
from pprint import pprint
from typing import List

from valcheck import fields, models, validator


ITEM_NAMES = ("Apple", "Banana", "Lemon", "Orange", "Bar of chocolate (100 grams)")
ITEM_UNITS = ("lbs", "kgs", "grams", "count")


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

    def model_validator(self) -> List[models.Error]:
        errors = []
        quantity = self.get_field_value('quantity')
        unit = self.get_field_value('unit')
        if unit == 'count' and not isinstance(quantity, int):
            message = "Since you selected `unit` as 'count', please ensure that `quantity` is an integer"
            errors.append(models.Error(details={"message": message}))
        return errors


class CartValidator(validator.Validator):
    customer_name = fields.StringField(allow_empty=False)
    timestamp_of_purchase = fields.DatetimeStringField(
        format_="%Y-%m-%d %H:%M:%S",
        converter_factory=lambda ts_string: datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S"),
    )
    items = fields.ModelListField(validator_model=ItemValidator, allow_empty=False)
    additional_info = fields.AnyField(required=False, nullable=True, default_factory=lambda: None)

    def model_validator(self):
        errors = []
        timestamp_of_purchase: datetime = self.get_field_value('timestamp_of_purchase')
        items = self.get_field_value('items')
        hour_of_day = timestamp_of_purchase.hour
        num_items = len(items)
        if 17 <= hour_of_day < 22 and num_items < 3:
            message = f"We expect you to add atleast 3 items while shopping between 5pm - 10pm. Received only {num_items} item/s"
            errors.append(models.Error(details={"message": message}))
        return errors


if __name__ == "__main__":
    data = {
        "customer_name": "Sundar Pichai",
        "timestamp_of_purchase": "2023-02-18 17:45:30",
        "items": [
            {
                "name": "Banana",
                "quantity": 1.5,
                "unit": "kgs",
            },
            {
                "name": "Bar of chocolate (100 grams)",
                "quantity": 2,
                "unit": "count",
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
        "additional_info": None,
    }
    cart_validator = CartValidator(data=data)
    errors = cart_validator.run_validations()
    if errors:
        pprint([error.as_dict() for error in errors]) # Error list
    else:
        pprint(cart_validator.validated_data) # Dictionary having validated data (by field)

