from itertools import groupby


from src.data_container import TimeSeries
from src.data_utils import DataUtils

import matplotlib.pyplot as plt
import pandas as pd


def load_reports():
    st_dev = 3.5

    parsers = {
        'Date': DataUtils.parse_date,
        'Last Price': DataUtils.parse_float
    }
    csv_files = {
        "eq_raw": r"C:\Users\naked\PycharmProjects\bh\resources/Equity_history_raw.csv",
        "eq_clean": r"C:\Users\naked\PycharmProjects\bh\resources/Equity_history_clean.csv",
        "fx_raw": r"C:\Users\naked\PycharmProjects\bh\resources/FX_history_raw.csv",
        "fx_clean": r"C:\Users\naked\PycharmProjects\bh\resources/FX_history_clean.csv",
        "ir_raw": r"C:\Users\naked\PycharmProjects\bh\resources/InterestRate_history_raw.csv",
        "ir_clean": r"C:\Users\naked\PycharmProjects\bh\resources/InterestRate_history_clean.csv",
    }

    data_containers = {k: DataUtils.read_csv(v, parsers) for k, v in csv_files.items()}

    for name, dc in data_containers.items():
        ts = TimeSeries(dc["Date"], dc["Last Price"])
        rem_na, na_count = DataUtils.forward_fill_na(ts.prices)
        rem_zeros, zero_count = DataUtils.forward_fill_val(rem_na, 0.)
        pc = DataUtils.pct_change(rem_zeros)

        pc, a = DataUtils.forward_fill_na(pc)
        zcs = DataUtils.ew_zsc(pc)
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
        clean, nas = DataUtils.forward_fill_na(ts.prices)
        clean, zeros = DataUtils.forward_fill_val(clean, 0.)
        for i in out_idx:
            clean[i] = clean[i-1]

        pc = DataUtils.pct_change(clean)
        pc, a = DataUtils.forward_fill_na(pc)
        zcs = DataUtils.ew_zsc(pc)
        out = [idx for idx, z in enumerate(zcs) if abs(z) > st_dev]
        out_idx2 =[]
        for k, g in groupby(enumerate(out), lambda t: t[1] - t[0]):
            l = list(g)
            if len(l) == 2:
                z1 = zcs[l[0][1]]
                z2 = zcs[l[1][1]]
                if abs(z2 - z1) > 2 * st_dev:
                    out_idx2.append(l[0][1])
        for i in out_idx2:
            clean[i] = clean[i-1]

        total = nas + zeros + len(out_idx) + len(out_idx2)
        print(total)
        pd.Series(clean).plot(title=name)
        plt.show()


load_reports()
