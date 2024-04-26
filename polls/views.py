from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.utils import timezone, timesince
from .models import Rate


def index(request):
    latest_rates = Rate.objects.order_by('-timestamp')
    exchanges = {}
    for rate in latest_rates:
        key = f'{rate.base_currency}->{rate.target_currency}'
        if key not in exchanges:
            exchanges[key] = rate.id
        else:
            latest_rates = latest_rates.exclude(id=rate.id)

    context = {
        'latest_rates': latest_rates
    }
    return render(request, 'polls/index.html', context)


def latest_rate(request, base_currency, target_currency):
    try:
        rates = Rate.objects.filter(base_currency=base_currency, target_currency=target_currency)
        if len(rates) < 1:
            raise Rate.DoesNotExist
        latest = rates[0].rate
        timestamp = rates[0].timestamp
        for rate in rates:
            if rate.timestamp > timestamp:
                latest = rate.rate
                timestamp = rate.timestamp

        context = {
            'base_currency': base_currency,
            'target_currency': target_currency,
            'rate': latest,
            'timestamp': timestamp,
        }
    except Rate.DoesNotExist:
        raise Http404(f'No exchange checked from {base_currency} to {target_currency}')
    return render(request, 'polls/latest_exchange.html', context)
