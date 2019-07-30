import datetime
from typing import List, Tuple

import src.data_utils as du
from src.time_series import TimeSeries


def clean_returns(returns, outlier_func, arg_list):
    rem_na, na_c = du.forward_fill_na(returns, val=0.)
    outliers = []
    cleaned = rem_na
    for n, t in arg_list:
        return_outliers = outlier_func(cleaned, n, t)
        underlying_outliers = du.find_first_in_pair(return_outliers)
        outliers.append(underlying_outliers)
        cleaned = du.fill_returns_outliers(cleaned, underlying_outliers)
    return outliers, cleaned


def check_file_data(file_path: str) -> List[Tuple[datetime.date, float, str]]:
    column_parsers = {
        'Date': du.parse_date,
        'Last Price': du.parse_float
    }

    mad_pass_thresholds = [(10, 20), (100, 10)]
    iqr_pass_thresholds = [(200, 10)]
    ewz_pass_thresholds = [(0.05, 5.5)]

    data = du.read_csv(file_path, column_parsers)
    ts = TimeSeries(data["Date"], data["Last Price"])

    rem_na, missing_na = du.forward_fill_na(ts.prices)
    no_zeros, missing_zeros = du.forward_fill_zeros(rem_na)

    all_outliers = [(ts.dates[i], ts.prices[i], "Missing - NA") for i in missing_na]
    all_outliers += [(ts.dates[i], ts.prices[i], "Missing - Zero") for i in missing_zeros]

    pc = du.pct_change(no_zeros)
    pc, _ = du.forward_fill_na(pc, 0.)

    mad_outliers, cleaned = clean_returns(pc, du.outliers_mad, mad_pass_thresholds)
    iqr_outliers, cleaned = clean_returns(cleaned, du.outliers_iqr, iqr_pass_thresholds)
    ewz_outliers, cleaned = clean_returns(cleaned, du.outliers_zcs, ewz_pass_thresholds)

    all_outliers += [(ts.dates[i], ts.prices[i], "Outlier - MAD") for s in mad_outliers for i in s]
    all_outliers += [(ts.dates[i], ts.prices[i], "Outlier - IQR") for s in iqr_outliers for i in s]
    all_outliers += [(ts.dates[i], ts.prices[i], "Outlier - EWZ") for s in ewz_outliers for i in s]

    stale_dates = du.stale_data(ts.prices, ts.dates, datetime.timedelta(weeks=1))

    all_outliers += [(sd[1], ts.prices[sd[0]], "Stale Data") for sd in stale_dates]

    return all_outliers

