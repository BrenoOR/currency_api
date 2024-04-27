from django.apps import AppConfig


class ExchangeRatesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "exchange_rates"

    def ready(self):
        from .currency_checker import update
        update.start()
