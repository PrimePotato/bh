import csv
import datetime
import math
import random
from collections import defaultdict, deque
from typing import List

tol = 1e-14


def read_csv(file_name: str, parsers: dict) -> dict:
    with open(file_name) as csvFile:
        reader = csv.DictReader(csvFile)
        data = defaultdict(list)
        [[data[k].append(v) for k, v in row.items()] for row in reader]
    return {k: [parsers[k](l) for l in v] for k, v in data.items()}


def parse_date(dt: str) -> datetime:
    d = [int(x) for x in dt.split("/")]
    return datetime.datetime(d[2], d[1], d[0])


def parse_float(d: str) -> float:
    # Todo: try except
    if d == '':
        return float('nan')
    else:
        return float(d)


def stale_data(series: List[float], dates: List[datetime.datetime],
               time_delta: datetime.timedelta = datetime.timedelta(weeks=1)):
    prev_p = float('nan')
    prev_d = datetime.datetime(1900, 1, 1)
    dt_windows = []
    s_dates = []
    for i, (d, p) in enumerate(zip(dates, series)):
        if abs(p - prev_p) < 1e-14:
            dt_windows.append((i - 1, prev_d))
            dt_windows.append((i, d))
            if dt_windows[-1][1] - dt_windows[0][1] >= time_delta:
                s_dates += dt_windows
        else:
            dt_windows = []
        prev_p = p
        prev_d = d
    stale_dates = sorted(set(s_dates))
    return stale_dates


def pct_change(series: List[float]) -> List[float]:
    prev = deque(series)
    prev.rotate(1)
    prev[0] = float('nan')
    return [(n - p) / n if n != 0 else float('nan') for n, p in zip(series, prev)]


def ew_ma(series: List[float], decay: float = 0.01) -> List[float]:
    result = [float('nan')] * len(series)
    result[0] = series[0]
    for i in range(1, len(series)):
        result[i] = series[i] * decay + (1 - decay) * result[i - 1]
    return result


def ew_var(series: List[float], decay: float = 0.01) -> List[float]:
    ewma = ew_ma(series, decay)
    diff = [0.01]
    for i in range(1, len(ewma)):
        d = (series[i] - ewma[i - 1])
        diff.append(d * d)
    return ew_ma(diff, decay)


def ew_std(series: List[float], decay: float = 0.01) -> List[float]:
    return [math.sqrt(x) for x in ew_var(series, decay)]


def ew_zsc(series: List[float], decay: float = 0.01) -> List[float]:
    ma = deque(ew_ma(series, decay))
    ma.rotate(1)
    ma[0] = ma[1]
    std = deque(ew_std(series, decay))
    std.rotate(1)
    std[0] = std[1]
    return [(s - a) / v for s, a, v in zip(series, ma, std)]


def forward_fill_na(series: List[float]):
    cleaned = []

    last_val = float('nan')
    for s in series:
        if s == s and abs(s) < tol:  # TODO: check zero is OK assumption to make
            last_val = s
            break

    i = 0
    for s in series:
        if s == s:
            last_val = s
            i += 1
        cleaned.append(last_val)
    return cleaned, len(cleaned) - i


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


def median(l, pivot_fn=random.choice):
    if len(l) % 2 == 1:
        return partition_select(l, (len(l) - 1) / 2, pivot_fn)
    else:
        return 0.5 * (partition_select(l, len(l) / 2 - 1, pivot_fn) +
                      partition_select(l, len(l) / 2, pivot_fn))


def partition_select(data, k, pivot_fn):
    if len(data) == 1:
        assert k == 0
        return data[0]
    p = pivot_fn(data)
    lower = [d for d in data if d < p]
    higher = [d for d in data if d > p]
    pivots = [d for d in data if d == p]

    if k < len(lower):
        return partition_select(lower, k, pivot_fn)
    elif k < len(lower) + len(pivots):
        return pivots[0]
    else:
        return partition_select(higher, k - len(lower) - len(pivots), pivot_fn)


def quartiles(data):
    m = median(data)
    ql = median([d for d in data if d <= m])
    qh = median([d for d in data if d >= m])
    return ql, qh


def rolling_window_apply(data, func, n=10):
    return [func(data[i:i + n]) for i in range(len(data) - n + 1)]


def iqr_bounds(data, k=1.5):
    m = median(data)
    l, h = quartiles(data)
    return m - k * (m - l), m + k * (h - m)
