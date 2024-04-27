from apscheduler.schedulers.background import BackgroundScheduler
from exchange_rates.models import Checker
from exchange_rates.currency_checker import checker


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(checker.update_currency_exchange,'interval',seconds=1)

    scheduler.start()
