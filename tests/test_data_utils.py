import logging
import os
from unittest import TestCase

from definitions import ROOT_DIR, CSV_PATHS, DataSource
from src.time_series import TimeSeries
from src.data_utils import *


class TestDataUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hdr_date = "Date"
        cls.hdr_last_price = "Last Price"

        cls.mock_outlier_series = [random.gauss(0, 0.1) for _ in range(100)] + [random.gauss(1e6, 1)] + [
            random.gauss(0, 0.1) for _ in range(100)]

        cls.parsers = {
            cls.hdr_date: parse_date,
            cls.hdr_last_price: parse_float
        }
        cls.data = {k: read_csv(p, cls.parsers) for k, p in CSV_PATHS.items()}

    def test_read_csv(self):
        self.assertEqual(len(self.data[DataSource.EQ_CLEAN]), 2)
        self.assertEqual(len(self.data[DataSource.EQ_CLEAN][self.hdr_date]),
                         len(self.data[DataSource.EQ_CLEAN][self.hdr_last_price]))
        self.assertTrue(isinstance(self.data[DataSource.EQ_CLEAN][self.hdr_date][0], datetime.datetime))
        self.assertTrue(isinstance(self.data[DataSource.EQ_CLEAN][self.hdr_last_price][0], float))

    def test_parse_date(self):
        self.assertEqual(parse_date("11/12/2019"), datetime.datetime(2019, 12, 11))

    def test_parse_float(self):
        self.assertEqual(parse_float("5.6123"), 5.6123)

    def test_stale_data(self):
        for k, v in self.data.items():
            tr = TimeSeries(v[self.hdr_date], v[self.hdr_last_price])
            dr = stale_data(tr.prices, tr.dates, datetime.timedelta(weeks=1))
            logging.info(str(k) + " raw " + str(len(dr)) + " " + str([tr.dates[i] for i, d in dr]) + " "
                         + str([tr.prices[i] for i, d in dr]))

    def test_pct_change(self):
        pct = pct_change(self.data[DataSource.EQ_CLEAN][self.hdr_last_price])
        pass

    def test_ewma(self):
        ewma = ew_ma(self.data[DataSource.EQ_CLEAN][self.hdr_last_price])
        self.assertEqual(len(ewma), len(self.data[DataSource.EQ_CLEAN][self.hdr_last_price]))
        self.assertAlmostEqual(ewma[-1], 5430.600493220166, delta=1e-14)

    def test_ew_var(self):
        pass
        # ew_var = ew_var(self.data[DataSource.EQ_CLEAN][self.hdr_last_price])
        # self.assertEqual(len(ew_var), len(self.data[self.hdr_last_price]))
        # self.assertAlmostEqual(ew_var[-1], 5319.445113673711, delta=1e-14)

    def test_ew_std(self):
        # ew_zsc = ew_zsc(pc)
        pass

    def test_ew_zsc(self):
        # ew_zsc = ew_zsc(pc)
        pass

    def test_forward_fill_na(self):
        cleaned = forward_fill_na(self.data[DataSource.EQ_CLEAN][self.hdr_last_price])
        self.assertEqual(len([c for c in cleaned if c != c]), 0)

    def test_forward_fill_val(self):
        cleaned = forward_fill_na(self.data[DataSource.EQ_CLEAN][self.hdr_last_price])
        self.assertEqual(len([c for c in cleaned if c != c]), 0)

    def test_median(self):
        self.assertEqual(median([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 6)
        self.assertAlmostEqual(median([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), 6.5)

    def test_partition_select(self):
        l = [9, 8, 7, 6, 5, 4, 3, 2, 1]
        partition_select(l, 4, lambda x: x[0])
        self.assertEqual(1, 1)

    def test_quartiles(self):
        pass

    def test_rolling_window_apply(self):
        s = 100
        n = 10
        f = sum
        data = list(range(1, s))
        w = rolling_window_apply(data, f, n=n)
        self.assertEqual(len(w), s)
        self.assertEqual(w[-1], f(range(s - n, s)))

    def test_iqr_bounds(self):
        data = [20, 15, 10, 5, 0]
        l, h = iqr_bounds(data)
        self.assertEqual(l, -15)
        self.assertEqual(h, 35)

    def test_mad_z_score(self):
        data = list(range(1, 50))
        mzs = mad_z_score(data)

    def test_outliers_mad(self):
        i = outliers_mad(self.mock_outlier_series)
        self.assertEqual(i[0], 100)

    def test_outliers_iqr(self):
        i = outliers_iqr(self.mock_outlier_series, k=10)
        self.assertEqual(i[0], 100)

    def test_outliers_zcs(self):
        i = outliers_zcs(self.mock_outlier_series)
        self.assertEqual(i[0], 100)
    # self.mock_outlier_series[i[0]]
