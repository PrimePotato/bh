from itertools import groupby

from definitions import DataSource, CSV_PATHS
from src.data_container import TimeSeries
import src.data_utils as du

import matplotlib.pyplot as plt
import pandas as pd

import logging

def load_reports():
    st_dev = 5

    parsers = {
        'Date': du.parse_date,
        'Last Price': du.parse_float
    }
    csv_files = {
        "eq_raw": r"C:\Users\naked\PycharmProjects\bh\resources/Equity_history_raw.csv",
        "eq_clean": r"C:\Users\naked\PycharmProjects\bh\resources/Equity_history_clean.csv",
        "fx_raw": r"C:\Users\naked\PycharmProjects\bh\resources/FX_history_raw.csv",
        "fx_clean": r"C:\Users\naked\PycharmProjects\bh\resources/FX_history_clean.csv",
        "ir_raw": r"C:\Users\naked\PycharmProjects\bh\resources/InterestRate_history_raw.csv",
        "ir_clean": r"C:\Users\naked\PycharmProjects\bh\resources/InterestRate_history_clean.csv",
    }

    data_containers = {k: du.read_csv(v, parsers) for k, v in csv_files.items()}

    for name, dc in data_containers.items():
        ts = TimeSeries(dc["Date"], dc["Last Price"])
        rem_na, na_count = du.forward_fill_na(ts.prices)
        rem_zeros, zero_count = du.forward_fill_val(rem_na, 0.)
        pc = du.pct_change(rem_zeros)

        pc, a = du.forward_fill_na(pc)
        zcs = du.ew_zsc(pc)
        out = [idx for idx, z in enumerate(zcs) if abs(z) > st_dev]
        out_idx = []
        for k, g in groupby(enumerate(out), lambda t: t[1] - t[0]):
            l = list(g)
            if len(l) == 2:
                z1 = zcs[l[0][1]]
                z2 = zcs[l[1][1]]
                if abs(z2 - z1) > 2 * st_dev:
                    out_idx.append(l[0][1])

        ts = TimeSeries(dc["Date"], dc["Last Price"])
        clean, nas = du.forward_fill_na(ts.prices)
        clean, zeros = du.forward_fill_val(clean, 0.)
        for i in out_idx:
            clean[i] = clean[i - 1]

        pc = du.pct_change(clean)
        pc, a = du.forward_fill_na(pc)
        zcs = du.ew_zsc(pc)
        out = [idx for idx, z in enumerate(zcs) if abs(z) > st_dev]
        out_idx2 = []
        for k, g in groupby(enumerate(out), lambda t: t[1] - t[0]):
            l = list(g)
            if len(l) == 2:
                z1 = zcs[l[0][1]]
                z2 = zcs[l[1][1]]
                if abs(z2 - z1) > 2 * st_dev:
                    out_idx2.append(l[0][1])
        for i in out_idx2:
            clean[i] = clean[i - 1]

        total = nas + zeros + len(out_idx) + len(out_idx2)
        print(total)
        pd.Series(clean).plot(title=name)
        plt.show()


def load_reports2():
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

        mad_outliers = []
        mad_pass = no_zeros
        for n, t in mad_pass_thresholds:
            mad_pass, c = du.forward_fill_mad(mad_pass, n, t)
            mad_outliers.append(c)

        iqr_outliers = []
        iqr_pass = mad_pass
        for n, k in iqr_pass_thresholds:
            iqr_pass, c = du.forward_fill_iqr(iqr_pass, n, k)
            iqr_outliers.append(c)

        ewz_outliers = []
        ewz_pass = iqr_pass
        for d, t in ewz_pass_thresholds:
            ewz_pass, c = du.forward_fill_zcs(ewz_pass, d, t)
            ewz_outliers.append(c)

        total = {
            'total': na_count + sum(mad_outliers) + sum(ewz_outliers) + sum(iqr_outliers) + zero_count,
            'na_count': na_count,
            'mad_count': mad_outliers,
            'iqr_count': iqr_outliers,
            'ewz_count': ewz_outliers,
            'zero_count': zero_count
        }
        logging.info(name.name + " " + str(total))

load_reports2()
