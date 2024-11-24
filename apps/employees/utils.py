import datetime
from calendar import monthrange


class Year(datetime.date):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def year(cls):
        today = datetime.date.today()
        return today.year

    @classmethod
    def get_days(cls, year, month):
        _, day_of_month = monthrange(year, month)
        return day_of_month
