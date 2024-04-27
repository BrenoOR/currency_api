import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from exchange_rates.models import Rate, Checker


def _get_current_currency_exchange(base_currency, target_currency):
    checker = Checker.objects.filter(base_currency=base_currency,
                                     target_currency=target_currency)
    rates = Rate.objects.filter(base_currency=base_currency,
                                target_currency=target_currency).order_by('-timestamp')
    if len(rates) > 0:
        if timezone.now() - rates[0].timestamp > checker[0].check_period:
            url = f'https://www.google.com/finance/quote/{base_currency}-{target_currency}'
            r = requests.get(url)
            timestamp = timezone.now()
            soup = BeautifulSoup(r.content, 'html.parser')
            rate = 0.0
            for div in soup.select('div'):
                if 'data-source' in div.attrs:
                    if div.attrs['data-source'] == base_currency and div.attrs['data-target'] == target_currency:
                        rate = div.attrs['data-last-price']
            return Rate(base_currency=base_currency, target_currency=target_currency, rate=rate, timestamp=timestamp)
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
        return Rate(base_currency=base_currency, target_currency=target_currency, rate=rate, timestamp=timestamp)


def update_currency_exchange():
    checkers = Checker.objects.all()
    for c in checkers:
        new_rate = _get_current_currency_exchange(base_currency=c.base_currency, target_currency=c.target_currency)
        new_rate.save()
