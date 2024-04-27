import uuid
from django.db import models


class Checker(models.Model):
    """
    The main model class to represent a currency exchange on database.

    ...
    Attributes
    ------------
    id : A unique identifier auto generated.
    base_currency : The base currency of the exchange.
    target_currency : The target currency of the exchange.
    check_period : The time between checks.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    check_period = models.DurationField('check period')

    def __str__(self):
        return f'{self.base_currency}$ -> {self.target_currency}$: Checks every {self.check_period}'


class Rate(models.Model):
    """
    The main model class to represent a currency exchange on database.

    ...
    Attributes
    ------------
    id : A unique identifier auto generated.
    base_currency : The base currency of the exchange.
    target_currency : The target currency of the exchange.
    rate : The exchange rate.
    timestamp : The exact date and time that the exchange rate was checked.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.FloatField()
    timestamp = models.DateTimeField('date checked')

    def __str__(self):
        return f'({self.timestamp}) {self.base_currency}$ 1 -> {self.target_currency}$ {self.rate}'
