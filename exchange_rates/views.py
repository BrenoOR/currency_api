from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
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


class LatestRateView(generic.ListView):
    model = Rate
    template_name = 'exchange_rates/latest_exchange.html'
    context_object_name = 'latest_rate'

    def get_queryset(self):
        rates = Rate.objects.filter(base_currency=self.kwargs['base_currency'],
                                    target_currency=self.kwargs['target_currency'])
        if len(rates) < 1:
            raise Rate.DoesNotExist
        timestamp = rates[0].timestamp
        latest_rate = rates[0]
        for rate in rates:
            if rate.timestamp > timestamp:
                latest_rate = rate
                timestamp = rate.timestamp
        return latest_rate


class HistoricalDataView(generic.ListView):
    template_name = 'exchange_rates/historical_data.html'
    context_object_name = 'rates'

    def get_queryset(self):
        rates = Rate.objects.filter(base_currency=self.kwargs['base_currency'],
                                    target_currency=self.kwargs['target_currency'])
        if len(rates) < 1:
            raise Rate.DoesNotExist

        return rates.order_by('-timestamp')
