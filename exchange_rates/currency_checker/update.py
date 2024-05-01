from apscheduler.schedulers.background import BackgroundScheduler
from exchange_rates.currency_checker import checker


def start():
    """
    The Scheduler start point.
    It runs the updater based on the given interval.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(checker.update_currency_exchange, 'interval', seconds=1)

    scheduler.start()
