import datetime
import random
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.test.utils import setup_test_environment
from django.test import Client

from .models import Rate


def create_exchange_rate(base_currency, target_currency, rate, time_offset):
    time = timezone.now() + datetime.timedelta(days=time_offset)
    return Rate.objects.create(base_currency=base_currency, target_currency=target_currency, rate=rate, timestamp=time)


class RateIndexViewTests(TestCase):
    def test_no_rates(self):
        """
        Return default message if no exchange rates are found.
        """
        response = self.client.get(reverse('exchange_rates:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No exchanges checked yet.')
        self.assertQuerySetEqual(response.context['latest_rates'], [])

    def test_only_latest_rate_per_exchange(self):
        """
        Return only one item for each exchange rates found.
        Based on base and target currencies.
        Eg.: If found multiple BRL->USD exchanges, index should show only the latest
        """
        create_exchange_rate('BRL', 'USD', 0.20, 1)
        create_exchange_rate('BRL', 'USD', 0.19, 1.2)
        brl_usd3 = create_exchange_rate('BRL', 'USD', 0.21, 1.7)
        create_exchange_rate('BRL', 'EUR', 0.19, 1)
        brl_eur2 = create_exchange_rate('BRL', 'EUR', 0.17, 1.2)
        response = self.client.get(reverse('exchange_rates:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['latest_rates'], [brl_usd3, brl_eur2])

#class RateLatestRateViewTests(TestCase):

