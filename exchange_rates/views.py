from django.core import serializers
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from django.views import generic

from .models import Rate


class IndexView(generic.ListView):
    template_name = 'exchange_rates/index.html'
    context_object_name = 'latest_rates'

    def get_queryset(self):
        latest_rates = Rate.objects.order_by('-timestamp')
        exchanges = {}
        for rate in latest_rates:
            key = f'{rate.base_currency}->{rate.target_currency}'
            if key not in exchanges:
                exchanges[key] = rate.id
            else:
                latest_rates = latest_rates.exclude(id=rate.id)
        return latest_rates


class ExchangeRateView(generic.ListView):
    model = Rate
    template_name = 'exchange_rates/exchange_rate.html'
    context_object_name = 'info'

    def get_queryset(self):
        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
        ).order_by('-timestamp')
        if len(rates) < 1:
            return {
                'latest_rate': None,
                'latest_rates': [],
                'value': None,
                'result': None,
            }
        latest_rates = Rate.objects.order_by('-timestamp')
        exchanges = {}
        for rate in latest_rates:
            key = f'{rate.base_currency}->{rate.target_currency}'
            if key not in exchanges:
                exchanges[key] = rate.id
            else:
                latest_rates = latest_rates.exclude(id=rate.id)
        return {
            'latest_rate': rates[0],
            'latest_rates': latest_rates,
            'value': float(self.kwargs['value']),
            'result': rates[0].rate * float(self.kwargs['value']),
        }


def calc_exchange(request, base_currency, target_currency, value):
    if request.method == 'POST':
        value = float(request.POST['BRL'].replace('$', '').replace(',', '.'))
        return HttpResponseRedirect(
            reverse(
                'exchange_rates:exchange_rate',
                args=(
                    base_currency,
                    target_currency,
                    value,
                ),
            )
        )


class LatestRateView(generic.ListView):
    model = Rate
    template_name = 'exchange_rates/latest_rate.html'
    context_object_name = 'rate'

    def get_queryset(self):
        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
        )
        if len(rates) < 1:
            raise Rate.DoesNotExist
        timestamp = rates[0].timestamp
        latest_rate = rates[0]
        for rate in rates:
            if rate.timestamp > timestamp:
                latest_rate = rate
                timestamp = rate.timestamp
        rate_js = {
            'base_currency': latest_rate.base_currency,
            'target_currency': latest_rate.target_currency,
            'rate': latest_rate.rate,
            'timestamp': latest_rate.timestamp,
        }
        return rate_js


def convert_tz(date_str):
    return timezone.make_aware(timezone.datetime.strptime(date_str, '%Y-%m-%d'))


class HistoricalDataView(generic.ListView):
    template_name = 'exchange_rates/historical_data.html'
    context_object_name = 'info'

    def get_queryset(self):
        start_date = self.kwargs['start_date']
        end_date = self.kwargs['end_date']
        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
        ).order_by('timestamp')
        if start_date == '0':
            if len(rates) > 0:
                start_date = rates[0].timestamp
            else:
                start_date = timezone.now()
        else:
            start_date = convert_tz(start_date)
        if end_date == '0':
            if len(rates) > 0:
                end_date = rates[len(rates)-1].timestamp
            else:
                end_date = timezone.now()
        else:
            end_date = convert_tz(end_date)
        if start_date > end_date:
            aux = start_date
            start_date = end_date
            end_date = aux

        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
            timestamp__gte=start_date,
            timestamp__lte=end_date,
        ).order_by('-timestamp')
        latest_rates = Rate.objects.order_by('-timestamp')
        exchanges = {}
        for rate in latest_rates:
            key = f'{rate.base_currency}->{rate.target_currency}'
            if key not in exchanges:
                exchanges[key] = rate.id
            else:
                latest_rates = latest_rates.exclude(id=rate.id)
        return {'base': self.kwargs['base_currency'], 'target': self.kwargs['target_currency'], 'history': rates,
                'latest_rates': latest_rates}


def set_history(request, base_currency, target_currency):
    if request.method == 'POST':
        start = request.POST['start']
        end = request.POST['end']
        if not start or start == '':
            start = '0'
        if not end or end == '':
            end = '0'
        return HttpResponseRedirect(
            reverse(
                'exchange_rates:historical_data',
                args=(
                    base_currency,
                    target_currency,
                    start,
                    end,
                ),
            )
        )


class HistoricalDataJSView(generic.ListView):
    model = Rate
    template_name = 'exchange_rates/historical_data_js.html'
    context_object_name = 'history'

    def get_queryset(self):
        start_date = self.kwargs['start_date']
        end_date = self.kwargs['end_date']
        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
        ).order_by('timestamp')
        if start_date == '0':
            if len(rates) > 0:
                start_date = rates[0].timestamp
            else:
                start_date = timezone.now()
        else:
            start_date = convert_tz(start_date)
        if end_date == '0':
            if len(rates) > 0:
                end_date = rates[len(rates)-1].timestamp
            else:
                end_date = timezone.now()
        else:
            end_date = convert_tz(end_date)
        if start_date > end_date:
            aux = start_date
            start_date = end_date
            end_date = aux

        rates = Rate.objects.filter(
            base_currency=self.kwargs['base_currency'],
            target_currency=self.kwargs['target_currency'],
            timestamp__gte=start_date,
            timestamp__lte=end_date,
        ).order_by('-timestamp')
        rates_js = []
        for rate in rates:
            rates_js.append({
                'base_currency': rate.base_currency,
                'target_currency': rate.target_currency,
                'rate': rate.rate,
                'timestamp': rate.timestamp,
            })
        return rates_js
