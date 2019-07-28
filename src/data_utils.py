import csv
import datetime
import math
from collections import defaultdict, deque
from typing import List, Tuple


class DataUtils:
    tol = 1e-14

    @staticmethod
    def read_csv(file_name: str, parsers: dict) -> dict:
        with open(file_name) as csvFile:
            reader = csv.DictReader(csvFile)
            data = defaultdict(list)
            [[data[k].append(v) for k, v in row.items()] for row in reader]
        return {k: [parsers[k](l) for l in v] for k, v in data.items()}

    @staticmethod
    def parse_date(dt: str) -> datetime:
        d = [int(x) for x in dt.split("/")]
        return datetime.datetime(d[2], d[1], d[0])

    @staticmethod
    def parse_float(d: str) -> float:
        # Todo: try except
        if d == '':
            return float('nan')
        else:
            return float(d)

    @staticmethod
    def findDateIndex(orginal, shifted):
        pass

    @staticmethod
    def stale_data(series: List[float], dates: List[datetime.datetime],
                   time_delta: datetime.timedelta = datetime.timedelta(weeks=1)):
        prev_p = float('nan')
        prev_d = datetime.datetime(1900, 1, 1)
        dt_windows = []
        stale_data = []
        for i, (d, p) in enumerate(zip(dates, series)):
            if abs(p - prev_p) < 1e-14:
                dt_windows.append((i-1, prev_d))
                dt_windows.append((i, d))
                if dt_windows[-1][1] - dt_windows[0][1] >= time_delta:
                    stale_data += dt_windows
            else:
                dt_windows = []
            prev_p = p
            prev_d = d
        stale_dates = sorted(set(stale_data))
        return stale_dates

    @staticmethod
    def pct_change(series: List[float]) -> List[float]:
        prev = deque(series)
        prev.rotate(1)
        prev[0] = float('nan')
        return [(n - p) / n if n != 0 else float('nan') for n, p in zip(series, prev)]

    @staticmethod
    def ew_ma(series: List[float], decay: float = 0.01) -> List[float]:
        result = [float('nan')] * len(series)
        result[0] = series[0]
        for i in range(1, len(series)):
            result[i] = series[i] * decay + (1 - decay) * result[i - 1]
        return result

    @staticmethod
    def ew_var(series: List[float], decay: float = 0.01) -> List[float]:
        ewma = DataUtils.ew_ma(series, decay)
        diff = [0.01]
        for i in range(1, len(ewma)):
            d = (series[i] - ewma[i-1])
            diff.append(d * d)
        ew_var = DataUtils.ew_ma(diff, decay)
        return ew_var

    @staticmethod
    def ew_std(series: List[float], decay: float = 0.01) -> List[float]:
        return [math.sqrt(x) for x in DataUtils.ew_var(series, decay)]

    @staticmethod
    def ew_zsc(series: List[float], decay: float = 0.01) -> List[float]:
        ew_ma = deque(DataUtils.ew_ma(series, decay))
        ew_ma.rotate(1)
        ew_ma[0] = ew_ma[1]
        ew_std = deque(DataUtils.ew_std(series, decay))
        ew_std.rotate(1)
        ew_std[0] = ew_std[1]
        return [(s - a) / v for s, a, v in zip(series, ew_ma, ew_std)]

    @staticmethod
    def forward_fill_na(series: List[float]):
        cleaned = []

        last_val = float('nan')
        for s in series:
            if s == s and abs(s) < DataUtils.tol:  # TODO: check zero is OK assumption to make
                last_val = s
                break

        i = 0
        for s in series:
            if s == s:
                last_val = s
                i += 1
            cleaned.append(last_val)
        return cleaned, len(cleaned) - i

    @staticmethod
    def forward_fill_val(series: List[float], val):
        cleaned = []
        last_val = float('nan')
        for s in series:
            if (s - val) > 1e-14:  # TODO: check zero is OK assumption to make, throw error
                last_val = s
                break
        i = 0
        for s in series:
            if abs(s - val) > 1e-14:
                last_val = s
                i += 1
            cleaned.append(last_val)
        return cleaned, len(cleaned) - i
