import datetime
import time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Rate, Checker
from .currency_checker import checker


class TestSetup:
    """
    A test setup class
    """

    def create_exchange_rate(self, base_currency, target_currency, rate, time_offset):
        """
        Auxiliary method that generates Rate objects.

        ...
        Attributes
        ------------
        base_currency : The base currency of the exchange.
        target_currency : The target currency of the exchange.
        rate : The exchange rate.
        time_offset : The time difference between the test time and the mocked object timestamp.
        """
        time = timezone.now() - datetime.timedelta(days=time_offset)
        return Rate.objects.create(
            base_currency=base_currency,
            target_currency=target_currency,
            rate=rate,
            timestamp=time,
        )

    def create_checker(self, base_currency, target_currency):
        """
        Auxiliary method that generates Checker objects.

        ...
        Attributes
        ------------
        base_currency : The base currency of the exchange.
        target_currency : The target currency of the exchange.
        """
        return Checker.objects.create(
            base_currency=base_currency,
            target_currency=target_currency,
            check_period=datetime.timedelta(seconds=1800),
        )

    def get_test_setup(self):
        """
        Method that creates mocked Rate objects.
        Exactly 5 Rate:
           3 of BRL -> USD
           2 of BRL -> EUR

        ...
        Returns
        ------------
        Latest Rate object of each kind
        """
        brl_usd = []
        brl_eur = []
        brl_usd.append(self.create_exchange_rate('BRL', 'USD', 0.20, 30))
        brl_usd.append(self.create_exchange_rate('BRL', 'USD', 0.19, 10.2))
        brl_usd3 = self.create_exchange_rate('BRL', 'USD', 0.21, 1.7)
        brl_eur.append(self.create_exchange_rate('BRL', 'EUR', 0.19, 10))
        brl_eur2 = self.create_exchange_rate('BRL', 'EUR', 0.17, 2.2)
        brl_usd.append(brl_usd3)
        brl_eur.append(brl_eur2)
        return brl_usd, brl_eur


class RateIndexViewTests(TestCase):
    def test_no_rates_should_return_proper_message(self):
        """
        Return default message if no exchange rates are found.
        """
        response = self.client.get(reverse('exchange_rates:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No exchanges checked yet.')
        self.assertQuerySetEqual(response.context['latest_rates'], [])

    def test_side_menu_should_show_only_latest_rate_per_exchange(self):
        """
        Return only one item for each exchange rates found.
        Based on base and target currencies.
        E.g.: If found multiple BRL->USD exchanges, index should show only the latest
        """
        test_setup = TestSetup().get_test_setup()
        brl_usd = test_setup[0]
        brl_eur = test_setup[1]
        response = self.client.get(reverse('exchange_rates:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['latest_rates'], [brl_usd[2], brl_eur[1]]
        )


class ExchangeRateViewTests(TestCase):
    def test_no_rates_should_return_proper_message(self):
        """
        Return default message if no exchange rates are found.
        """
        response = self.client.get(reverse('exchange_rates:exchange_rate',
                                           kwargs={'base_currency': 'BRL', 'target_currency': 'USD', 'value': '1'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No exchanges checked yet.')
        self.assertQuerySetEqual(response.context['info']['latest_rates'], [])

    def test_side_menu_should_show_only_latest_rate_per_exchange(self):
        """
        Return only one item for each exchange rates found.
        Based on base and target currencies.
        Eg.: If found multiple BRL->USD exchanges, index should show only the latest
        """
        test_setup = TestSetup().get_test_setup()
        brl_usd = test_setup[0]
        brl_eur = test_setup[1]
        response = self.client.get(reverse('exchange_rates:exchange_rate',
                                           kwargs={'base_currency': 'BRL', 'target_currency': 'USD', 'value': '1'}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['info']['latest_rates'], [brl_usd[2], brl_eur[1]]
        )

    def test_form_exchange_should_get_latest_rate_times_form_value(self):
        """
        Return the form value input * latest exchange rate.
        """
        test_setup = TestSetup().get_test_setup()
        response = self.client.get(reverse('exchange_rates:exchange_rate',
                                           kwargs={'base_currency': 'BRL', 'target_currency': 'USD', 'value': '1.5'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['info']['result'], 1.5 * test_setup[0][2].rate)

    def test_form_exchange_should_post_correct_value(self):
        """
        Post the updated value and retrieve the form updated value input * latest exchange rate.
        """
        test_setup = TestSetup().get_test_setup()
        response = self.client.post(path=reverse('exchange_rates:calc_exchange',
                                                 kwargs={
                                                     'base_currency': 'BRL',
                                                     'target_currency': 'USD',
                                                     'value': '1.5'
                                                 }),
                                    data={'BRL': '$1.7'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(response.url.split('/')), 4)
        none, base_currency, target_currency, value = response.url.split('/')
        redirect = self.client.get(reverse('exchange_rates:exchange_rate',
                                           kwargs={
                                               'base_currency': base_currency,
                                               'target_currency': target_currency,
                                               'value': value
                                           }))
        self.assertEqual(redirect.status_code, 200)
        self.assertEqual(redirect.context['info']['result'], 1.7 * test_setup[0][2].rate)


class LatestRateViewTests(TestCase):
    def test_request_should_respond_json(self):
        """
        Return a json-like info of only the latest exchange
        """
        test_setup = TestSetup().get_test_setup()
        response = self.client.get(reverse('exchange_rates:latest_rate',
                                           kwargs={'base_currency': 'BRL', 'target_currency': 'USD'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['rate'],
            {
                'base_currency': test_setup[0][2].base_currency,
                'target_currency': test_setup[0][2].target_currency,
                'rate': test_setup[0][2].rate,
                'timestamp': test_setup[0][2].timestamp
            }
        )

    def test_no_rates_should_return_404(self):
        """
        Return a 404 error
        """
        test_setup = TestSetup().get_test_setup()
        response = self.client.get(reverse('exchange_rates:latest_rate',
                                           kwargs={'base_currency': 'EUR', 'target_currency': 'USD'}))
        self.assertEqual(response.status_code, 404)


class HistoricalDataViewTests(TestCase):
    def test_no_rates_should_return_proper_message(self):
        """
        Return default message if no exchange rates are found.
        """
        response = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': '0',
                                               'end_date': '0'
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No exchanges checked yet.')
        self.assertQuerySetEqual(response.context['info']['latest_rates'], [])

    def test_side_menu_should_show_only_latest_rate_per_exchange(self):
        """
        Return only one item for each exchange rates found.
        Based on base and target currencies.
        E.g.: If found multiple BRL->USD exchanges, index should show only the latest
        """
        test_setup = TestSetup().get_test_setup()
        brl_usd = test_setup[0]
        brl_eur = test_setup[1]
        response = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': '0',
                                               'end_date': '0'
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['info']['latest_rates'], [brl_usd[2], brl_eur[1]]
        )

    def test_form_time_diff_should_get_all_rates_inside_interval(self):
        """
        Return all rates inside the given time interval.
        In this test, we insert 3 rates and should retrieve 2 rates only.
        """
        TestSetup().get_test_setup()
        start_date = timezone.now() - datetime.timedelta(days=15)
        end_date = timezone.now()
        response = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': start_date.strftime('%Y-%m-%d'),
                                               'end_date': end_date.strftime('%Y-%m-%d')
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['info']['history']), 2)

    def test_form_time_diff_inverted_should_get_all_rates_inside_interval(self):
        """
        Return all rates inside the given time interval.
        In this test, we insert 3 rates and should retrieve 2 rates only.
        """
        TestSetup().get_test_setup()
        start_date = timezone.now() - datetime.timedelta(days=15)
        end_date = timezone.now()
        response = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': end_date.strftime('%Y-%m-%d'),
                                               'end_date': start_date.strftime('%Y-%m-%d')
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['info']['history']), 2)

    def test_form_time_diff_should_post_correct_time_diff(self):
        """
        Post updated time interval and retrieve all rates inside it.
        In this test, we insert 3 rates and should retrieve 2 rates only.
        """
        TestSetup().get_test_setup()
        start_date = timezone.now() - datetime.timedelta(days=15)
        end_date = timezone.now()
        response = self.client.post(path=reverse('exchange_rates:change_range',
                                                 kwargs={
                                                     'base_currency': 'BRL',
                                                     'target_currency': 'USD'
                                                 }),
                                    data={
                                        'start': start_date.strftime('%Y-%m-%d'),
                                        'end': end_date.strftime('%Y-%m-%d')
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(response.url.split('/')), 6)
        none, base_currency, target_currency, url_str, start_date_redi, end_date_redi = response.url.split('/')
        redirect = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': base_currency,
                                               'target_currency': target_currency,
                                               'start_date': start_date_redi,
                                               'end_date': end_date_redi
                                           }))
        self.assertEqual(redirect.status_code, 200)
        self.assertEqual(len(redirect.context['info']['history']), 2)

    def test_form_time_diff_no_info_should_post_correct_full_time_interval(self):
        """
        Post no time interval and retrieve all rates.
        In this test, we insert 3 rates and should retrieve 3 rates.
        """
        TestSetup().get_test_setup()
        response = self.client.post(path=reverse('exchange_rates:change_range',
                                                 kwargs={
                                                     'base_currency': 'BRL',
                                                     'target_currency': 'USD'
                                                 }),
                                    data={
                                        'start': '',
                                        'end': ''
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(response.url.split('/')), 6)
        none, base_currency, target_currency, url_str, start_date_redi, end_date_redi = response.url.split('/')
        redirect = self.client.get(reverse('exchange_rates:historical_data',
                                           kwargs={
                                               'base_currency': base_currency,
                                               'target_currency': target_currency,
                                               'start_date': start_date_redi,
                                               'end_date': end_date_redi
                                           }))
        self.assertEqual(redirect.status_code, 200)
        self.assertEqual(len(redirect.context['info']['history']), 3)


class HistoricalDataJSViewTests(TestCase):
    def test_no_rates_should_respond_empty_json(self):
        """
        Return an empty list
        """
        response = self.client.get(reverse('exchange_rates:historical_data_js',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': '0',
                                               'end_date': '0'
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['history'], []
        )

    def test_default_dates_should_respond_all_data(self):
        """
        Return a json-like info containing all rates
        """
        setup = TestSetup().get_test_setup()
        expected = []
        for rate in setup[0]:
            expected.insert(0,
                            {
                                'base_currency': rate.base_currency,
                                'target_currency': rate.target_currency,
                                'rate': rate.rate,
                                'timestamp': rate.timestamp
                            })
        response = self.client.get(reverse('exchange_rates:historical_data_js',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': '0',
                                               'end_date': '0'
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['history'], expected
        )

    def test_request_should_respond_json(self):
        """
        Return a json-like info containing all rates inside interval
        """
        setup = TestSetup().get_test_setup()
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=15)
        response = self.client.get(reverse('exchange_rates:historical_data_js',
                                           kwargs={
                                               'base_currency': 'BRL',
                                               'target_currency': 'USD',
                                               'start_date': end_date.strftime('%Y-%m-%d'),
                                               'end_date': start_date.strftime('%Y-%m-%d')
                                           }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['history'], [
                {
                    'base_currency': setup[0][2].base_currency,
                    'target_currency': setup[0][2].target_currency,
                    'rate': setup[0][2].rate,
                    'timestamp': setup[0][2].timestamp
                },
                {
                    'base_currency': setup[0][1].base_currency,
                    'target_currency': setup[0][1].target_currency,
                    'rate': setup[0][1].rate,
                    'timestamp': setup[0][1].timestamp
                }
            ]
        )


class CurrencyCheckerTests(TestCase):
    def test_exchange_checker_found_should_update_exchange_rate(self):
        """
        Verify if a currency exchange (Checker) does not have Rates or its out of date.
        It should retrieve a new rate.
        """
        TestSetup().get_test_setup()
        checker.update_currency_exchange()
        TestSetup().create_checker('BRL', 'USD')
        TestSetup().create_checker('BRL', 'EUR')
        time.sleep(1)
        checker.update_currency_exchange()
        checkers = Checker.objects.all()
        rates = Rate.objects.all()
        self.assertEqual(len(checkers), 2)
        self.assertEqual(len(rates), 7)
        TestSetup().create_checker('USD', 'EUR')
        time.sleep(1)
        checker.update_currency_exchange()
        checkers = Checker.objects.all()
        rates = Rate.objects.all()
        self.assertEqual(len(checkers), 3)
        self.assertEqual(len(rates), 8)

