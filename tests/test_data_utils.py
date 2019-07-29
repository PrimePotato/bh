import os
from unittest import TestCase

from definitions import ROOT_DIR
from src.data_container import TimeSeries
from src.data_utils import *


class TestDataUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hdr_date = "Date"
        cls.hdr_last_price = "Last Price"

        cls.parsers = {
            cls.hdr_date: parse_date,
            cls.hdr_last_price: parse_float
        }
        # ToDo: relative paths and os path join!
        cls.data_clean = {
            "eq": read_csv(os.path.join(ROOT_DIR, "resources", "Equity_history_clean.csv"), cls.parsers),
            "fx": read_csv(os.path.join(ROOT_DIR, "resources", "FX_history_clean.csv"), cls.parsers),
            "ir": read_csv(os.path.join(ROOT_DIR, "resources", "InterestRate_history_clean.csv"), cls.parsers)
        }

        cls.data_raw = {
            "eq": read_csv(os.path.join(ROOT_DIR, "resources", "Equity_history_raw.csv"), cls.parsers),
            "fx": read_csv(os.path.join(ROOT_DIR, "resources", "FX_history_raw.csv"), cls.parsers),
            "ir": read_csv(os.path.join(ROOT_DIR, "resources", "InterestRate_history_raw.csv"), cls.parsers)
        }

    def test_read_csv(self):
        self.assertEqual(len(self.data_clean['eq']), 2)
        self.assertEqual(len(self.data_clean['eq'][self.hdr_date]), len(self.data_clean['eq'][self.hdr_last_price]))
        self.assertTrue(isinstance(self.data_clean['eq'][self.hdr_date][0], datetime.datetime))
        self.assertTrue(isinstance(self.data_clean['eq'][self.hdr_last_price][0], float))

    def test_parse_date(self):
        self.assertEqual(parse_date("11/12/2019"), datetime.datetime(2019, 12, 11))

    def test_parse_float(self):
        self.assertEqual(parse_float("5.6123"), 5.6123)

    def test_stale_data(self):
        for k, v in self.data_raw.items():
            tr = TimeSeries(v[self.hdr_date], v[self.hdr_last_price])
            dr = stale_data(tr.prices, tr.dates, datetime.timedelta(weeks=1))
            print(str(k) + " raw " + str(len(dr)) + " " + str([tr.dates[i] for i, d in dr]) + " "
                  + str([tr.prices[i] for i, d in dr]))

        for k, v in self.data_clean.items():
            tc = TimeSeries(v[self.hdr_date], v[self.hdr_last_price])
            dc = stale_data(tc.prices, tc.dates, datetime.timedelta(weeks=1))
            print(str(k) + " clean " + str(len(dc)) + " " + str([tc.dates[i] for i, d in dc]) + " "
                  + str([tc.prices[i] for i, d in dc]))

    def test_pct_change(self):
        pct = pct_change(self.data_clean["eq"][self.hdr_last_price])
        pass

    def test_ewma(self):
        ewma = ew_ma(self.data_clean["eq"][self.hdr_last_price])
        self.assertEqual(len(ewma), len(self.data_clean["eq"][self.hdr_last_price]))
        self.assertAlmostEqual(ewma[-1], 5430.600493220166, delta=1e-14)

    def test_ew_var(self):
        pass
        # ew_var = ew_var(self.data_clean["eq"][self.hdr_last_price])
        # self.assertEqual(len(ew_var), len(self.data_clean[self.hdr_last_price]))
        # self.assertAlmostEqual(ew_var[-1], 5319.445113673711, delta=1e-14)

    def test_ew_std(self):
        # ew_zsc = ew_zsc(pc)
        pass

    def test_ew_zsc(self):
        # ew_zsc = ew_zsc(pc)
        pass

    def test_forward_fill_na(self):
        cleaned = forward_fill_na(self.data_clean["eq"][self.hdr_last_price])
        self.assertEqual(len([c for c in cleaned if c != c]), 0)

    def test_forward_fill_val(self):
        cleaned = forward_fill_na(self.data_clean["eq"][self.hdr_last_price])
        self.assertEqual(len([c for c in cleaned if c != c]), 0)

    def test_median(self):
        self.assertEqual(median([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 6)
        self.assertAlmostEqual(median([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]), 6.5)

    def test_partition_select(self):
        pass

    def test_parition(self):
        pass
