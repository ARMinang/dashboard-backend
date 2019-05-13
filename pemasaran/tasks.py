from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
import datetime
from pemasaran.fetch_lb import fetch_iuran
from pemasaran.fetch_tk import fetch_all_tk_baru
from pemasaran.fetch_npp import fetch_all_npp


logger = get_task_logger(__name__)


def fetch_lb_task():
    current_date = datetime.datetime.today().strftime("%d-%m-%Y")
    year_start = datetime.datetime.today().replace(month=1, day=1).strftime(
        "%d-%m-%Y"
    )
    ak_data = dict()
    ak_data["user"] = ""
    ak_data["periode1"] = year_start
    ak_data["periode2"] = current_date
    fetch_iuran(ak_data)
    logger.info("Fetch Iuran")


def fetch_tk_task():
    current_date = datetime.datetime.today().strftime("%d-%m-%Y")
    to_fetch = {"periode": current_date}
    fetch_all_tk_baru(to_fetch)
    logger.info("Fetch TK")


def fetch_npp_task():
    fetch_all_npp()
    logger.info("Fetch All NPP")


@periodic_task(
    run_every=(crontab(minute=0, hour='*/1')),
    name="Fetch Hourly Data",
    ignore_result=True
)
def fetch_all():
    fetch_npp_task()
    # fetch_lb_task()
    # fetch_tk_task()
