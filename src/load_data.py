import datetime
from itertools import groupby

from definitions import DataSource, CSV_PATHS
from src.data_container import TimeSeries
import src.data_utils as du

import matplotlib.pyplot as plt
import pandas as pd

import logging


def load_reports():
    mad_pass_thresholds = [
        (10, 20),
        (30, 12),
        (100, 10),
    ]

    iqr_pass_thresholds = [
        (20, 25),
        (50, 15)
    ]

    ewz_pass_thresholds = [
        (0.1, 5.5)
    ]

    column_parsers = {
        'Date': du.parse_date,
        'Last Price': du.parse_float
    }

    data_containers = {k: du.read_csv(v, column_parsers) for k, v in CSV_PATHS.items()}

    for name, dc in data_containers.items():
        ts = TimeSeries(dc["Date"], dc["Last Price"])
        rem_na, na_count = du.forward_fill_na(ts.prices)
        no_zeros, zero_count = du.forward_fill_zeros(rem_na)

        pc = du.pct_change(no_zeros)
        pc_rem_na, na_c = du.forward_fill_na(pc, val=0.)

        mad_outliers = []
        mad_pass = pc_rem_na
        for n, t in mad_pass_thresholds:
            outliers = du.outliers_mad(mad_pass, n, t)
            mad_outliers.append(outliers)
            du.forward_fill_outliers(mad_pass, outliers)

        iqr_outliers = []
        iqr_pass = mad_pass
        for n, k in iqr_pass_thresholds:
            outliers = du.outliers_iqr(iqr_pass, n, k)
            iqr_outliers.append(outliers)
            du.forward_fill_outliers(iqr_pass, outliers)

        ewz_outliers = []
        ewz_pass = iqr_pass
        for d, t in ewz_pass_thresholds:
            outliers = du.outliers_zcs(ewz_pass, d, t)
            ewz_outliers.append(outliers)
            du.forward_fill_outliers(ewz_pass, outliers)

        stale_dates = du.stale_data(ts.prices, ts.dates, datetime.timedelta(weeks=1))

        total = {
            'total': na_count + sum(mad_outliers) + sum(ewz_outliers) + sum(iqr_outliers) + len(
                stale_dates) + zero_count,
            'na_count': na_count,
            'mad_count': mad_outliers,
            'iqr_count': iqr_outliers,
            'ewz_count': ewz_outliers,
            'zero_count': zero_count,
            'stale_dates': (len(stale_dates), stale_dates)
        }
        pd.Series(ewz_pass).plot(title=name)
        plt.show()

        logging.info(name.name + " " + str(total))


load_reports()
