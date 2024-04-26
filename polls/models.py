import uuid
from django.db import models


class Rate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.FloatField()
    timestamp = models.DateTimeField("date checked")

    def __str__(self):
        return f'({self.timestamp}) {self.base_currency}$ 1 -> {self.target_currency}$ {self.rate}'
