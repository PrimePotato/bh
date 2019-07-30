import csv
import datetime
import math
import random
from collections import defaultdict, deque
from itertools import groupby
from typing import List, Tuple

tol = 1e-14


def read_csv(file_name: str, parsers: dict) -> dict:
    with open(file_name) as csvFile:
        reader = csv.DictReader(csvFile)
        data = defaultdict(list)
        [[data[k].append(v) for k, v in row.items()] for row in reader]
    return {k: [parsers[k](l) for l in v] for k, v in data.items()}


def parse_date(dt: str) -> datetime:
    try:
        d = [int(x) for x in dt.split("/")]
        return datetime.datetime(d[2], d[1], d[0])
    except ValueError:
        return None


def parse_float(d: str) -> float:
    try:
        return float(d)
    except ValueError:
        return float('nan')


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
    prev[0] = 0.
    return [(n - p) / p if n != 0 else float('nan') for n, p in zip(series, prev)]


def ew_ma(series: List[float], decay: float = 0.01) -> List[float]:
    result = [float('nan')] * len(series)
    result[0] = series[0]
    for i in range(1, len(series)):
        result[i] = series[i] * decay + (1 - decay) * result[i - 1]
    return result


def ew_var(series: List[float], decay: float = 0.01, initial=0.1) -> List[float]:
    ewma = ew_ma(series, decay)
    diff = [initial]
    for i in range(1, len(ewma)):
        d = (series[i] - ewma[i - 1])
        diff.append(d * d)
    return ew_ma(diff, decay)


def ew_std(series: List[float], decay: float = 0.01) -> List[float]:
    return [math.sqrt(x) for x in ew_var(series, decay)]


def fill_find_next(i, sorted_seq):
    for s in sorted_seq:
        if s > i:
            return s
    return sorted_seq[-1]


def outliers_mad(series, n=30, threshold=6):
    mad_z = rolling_window_apply(series, mad_z_score, n)
    mad_z_outliers = [i - 1 for i, x in enumerate(mad_z) if abs(x) > threshold]
    return find_first_in_pair(mad_z_outliers)


def find_first_in_pair(data):
    return [next(g)[1] for k, g in groupby(enumerate(data), lambda t: t[1] - t[0])]


def outliers_zcs(series, decay=0.01, threshold=6):
    ez = ew_zsc(series, decay)
    ez_outliers = [i for i, x in enumerate(ez) if abs(x) > threshold]
    return find_first_in_pair(ez_outliers)


def replace_outliers(series, outliers, value):
    return [value if i in outliers else s for i, s in enumerate(series)]


def outliers_iqr(series, n=30, k=5):
    qs = rolling_window_apply(series, lambda x: iqr_bounds(x, k), n, na_value=(float('nan'), float('nan')))
    qs_outliers = []
    for i, (s, (q1, q2)) in enumerate(zip(series, qs)):
        if s < q1 or q2 < s:
            qs_outliers.append(i)
    return find_first_in_pair(qs_outliers)


def forward_fill_outliers(series, outlier_indicies):
    good_indiicies = sorted(list(set(range(len(series))) - set(outlier_indicies)))
    try:
        filled = series.copy()
        for oi in outlier_indicies:
            ri = fill_find_next(oi, good_indiicies)
            filled[oi] = series[ri]
        return filled
    except Exception:
        return None


def ew_zsc(series: List[float], decay: float = 0.01) -> List[float]:
    ma = deque(ew_ma(series, decay))
    ma.rotate(1)
    ma[0] = ma[1]
    std = deque(ew_std(series, decay))
    std.rotate(1)
    std[0] = std[1]
    return [(s - a) / v for s, a, v in zip(series, ma, std)]


def forward_fill_na(series: List[float], val=None) -> Tuple[List[float], int]:
    cleaned = []
    last_val = float('nan')
    for s in series:
        if s == s and abs(s) < tol:  # TODO: check zero is OK assumption to make
            last_val = s
            break
    if val:
        for s in series:
            if s != s:
                cleaned.append(val)
            else:
                cleaned.append(s)
    else:
        i = 0
        for s in series:
            if s == s:
                last_val = s
                i += 1
            cleaned.append(last_val)
    return cleaned, len(cleaned) - i


def forward_fill_zeros(series: List[float]) -> Tuple[List[float], int]:
    return forward_fill_val(series, 0)


def forward_fill_val(series: List[float], val: float) -> Tuple[List[float], int]:
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
        return partition_select(l, int((len(l) - 1) / 2), pivot_fn)
    else:
        return 0.5 * (partition_select(l, int(len(l) / 2 - 1), pivot_fn) +
                      partition_select(l, int(len(l) / 2), pivot_fn))


def partition_select(data: List[float], k: int, pivot_fn) -> int:
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


def quartiles(data: List[float]):
    try:
        m = median(data)
        ql = median([d for d in data if d <= m])
        qh = median([d for d in data if d >= m])
    except Exception:
        pass
    return ql, qh


def rolling_window_apply(data, func, n=10, na_value=float('nan')):
    return [na_value] * n + [func(data[i:i + n]) for i in range(len(data) - n + 1)]


def iqr_bounds(data: List[float], k: float = 5) -> Tuple[float, float]:
    m = median(data)
    l, h = quartiles(data)
    return m - k * (m - l), m + k * (h - m)


def mad_z_score(data: List[float], min_dev=1e-14) -> float:
    try:
        m = median(data)
        mad = median([abs(y - m) for y in data])
        if mad < min_dev:
            return 0.
        return 0.67449 * (data[-1] - m) / mad
    except Exception:
        return 0.
