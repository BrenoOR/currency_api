import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from exchange_rates.models import Rate, Checker


def _get_current_currency_exchange(checker, base_currency, target_currency):
    """
    The generic currency checker.
    It checks if the last currency exchange is out of date, based on the Checker model's check period.
    """
    rates = Rate.objects.filter(base_currency=base_currency,
                                target_currency=target_currency).order_by('-timestamp')
    if len(rates) > 0:
        if timezone.now() - rates[0].timestamp > checker.check_period:
            url = f'https://www.google.com/finance/quote/{base_currency}-{target_currency}'
            r = requests.get(url)
            timestamp = timezone.now()
            soup = BeautifulSoup(r.content, 'html.parser')
            rate = 0.0
            for div in soup.select('div'):
                if 'data-source' in div.attrs:
                    if div.attrs['data-source'] == base_currency and div.attrs['data-target'] == target_currency:
                        rate = div.attrs['data-last-price']
            new_rate = Rate(base_currency=base_currency, target_currency=target_currency, rate=rate,
                            timestamp=timestamp)
            new_rate.save()
    else:
        url = f'https://www.google.com/finance/quote/{base_currency}-{target_currency}'
        r = requests.get(url)
        timestamp = timezone.now()
        soup = BeautifulSoup(r.content, 'html.parser')
        rate = 0.0
        for div in soup.select('div'):
            if 'data-source' in div.attrs:
                if div.attrs['data-source'] == base_currency and div.attrs['data-target'] == target_currency:
                    rate = div.attrs['data-last-price']
        new_rate = Rate(base_currency=base_currency, target_currency=target_currency, rate=rate, timestamp=timestamp)
        new_rate.save()


def update_currency_exchange():
    """
    The Scheduled updater.
    It runs a check for every Checker retrieved on database.
    """
    checkers = Checker.objects.all()
    for c in checkers:
        _get_current_currency_exchange(checker=c, base_currency=c.base_currency, target_currency=c.target_currency)
