import datetime
from itertools import groupby

from definitions import DataSource, CSV_PATHS
from src.time_series import TimeSeries
import src.data_utils as du

import matplotlib.pyplot as plt
import pandas as pd

import logging


def clean_data(ts: TimeSeries, mad_pass_thresholds, iqr_pass_thresholds, ewz_pass_thresholds):
    rem_na, na_count = du.forward_fill_na(ts.prices)
    no_zeros, zero_count = du.forward_fill_zeros(rem_na)

    pc = du.pct_change(no_zeros)
    pc_rem_na, na_c = du.forward_fill_na(pc, val=0.)
    mad_outliers = []
    mad_pass = pc_rem_na
    for n, t in mad_pass_thresholds:
        return_outliers = du.outliers_mad(mad_pass, n, t)
        underlying_outliers = du.find_first_in_pair(return_outliers)
        mad_outliers.append(underlying_outliers)
        mad_pass = du.fill_returns_outliers(mad_pass, underlying_outliers)


def load_reports():
    mad_pass_thresholds = [(10, 20), (30, 12), (100, 10)]

    iqr_pass_thresholds = [
        (50, 15),
        # (50, 15)
    ]

    ewz_pass_thresholds = [
        (0.1, 5.5)
    ]

    column_parsers = {
        'Date': du.parse_date,
        'Last Price': du.parse_float
    }

    data_containers = {k: du.read_csv(v, column_parsers) for k, v in CSV_PATHS.items()}
    issue_count = {}
    issue_details = {}

    for name, dc in data_containers.items():
        ts = TimeSeries(dc["Date"], dc["Last Price"])
        rem_na, na_count = du.forward_fill_na(ts.prices)
        no_zeros, zero_count = du.forward_fill_zeros(rem_na)

        pc = du.pct_change(no_zeros)
        pc_rem_na, na_c = du.forward_fill_na(pc, val=0.)

        mad_outliers = []
        mad_pass = pc_rem_na
        for n, t in mad_pass_thresholds:
            return_outliers = du.outliers_mad(mad_pass, n, t)
            underlying_outliers = du.find_first_in_pair(return_outliers)
            mad_outliers.append(underlying_outliers)
            mad_pass = du.fill_returns_outliers(mad_pass, underlying_outliers)

        iqr_outliers = []
        iqr_pass = mad_pass
        for n, k in iqr_pass_thresholds:
            return_outliers = du.outliers_iqr(iqr_pass, n, k)
            iqr_outliers.append(return_outliers)
            # du.forward_fill_outliers(iqr_pass, outliers)

        ewz_outliers = []
        ewz_pass = iqr_pass
        for d, t in ewz_pass_thresholds:
            return_outliers = du.outliers_zcs(ewz_pass, d, t)
            ewz_outliers.append(return_outliers)
            # du.forward_fill_outliers(ewz_pass, outliers)

        stale_dates = du.stale_data(ts.prices, ts.dates, datetime.timedelta(weeks=1))

        mad_count = sum([len(s) for s in mad_outliers])
        iqr_count = sum([len(s) for s in iqr_outliers])
        ewz_count = sum([len(s) for s in ewz_outliers])

        issue_count[name] = {
            'total': na_count + 1 + len(stale_dates) + zero_count + mad_count + iqr_count + ewz_count,
            'na_count': na_count,
            'mad_count': mad_count,
            'iqr_count': iqr_count,
            'ewz_count': ewz_count,
            'zero_count': zero_count,
            'stale_dates': len(stale_dates)
        }

        details = {
            'stale_dates': stale_dates,
            'mad_outliers': mad_outliers,
            'iqr_outliers': iqr_outliers,
            'ewz_outliers': ewz_outliers,
        }

        pd.Series(ewz_pass).plot(title=name)
        plt.show()

        logging.info(name.name + " " + str(issue_count[name]))

    logging.info(str(issue_details))


load_reports()
