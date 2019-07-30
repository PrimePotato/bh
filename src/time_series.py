import datetime
from typing import List


class TimeSeries(object):
    def __init__(self, dates: List[datetime.date], prices: List[float]):
        s = sorted(zip(dates, prices), key=lambda x: x[0])
        self.dates, self.prices = list(zip(*s))
        self.dates, self.prices = list(self.dates), list(self.prices)
