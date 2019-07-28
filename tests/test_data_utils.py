import datetime
from unittest import TestCase

from src.data_container import TimeSeries
from src.data_utils import DataUtils


class TestDataUtils(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hdr_date = "Date"
        cls.hdr_last_price = "Last Price"

        cls.parsers = {
            cls.hdr_date: DataUtils.parse_date,
            cls.hdr_last_price: DataUtils.parse_float
        }
        # ToDo: relative paths and os path join!
        cls.data_clean = {
            "eq": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\Equity_history_clean.csv",
                                     cls.parsers),
            "fx": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\FX_history_clean.csv", cls.parsers),
            "ir": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\InterestRate_history_clean.csv",
                                     cls.parsers)
        }

        cls.data_raw = {
            "eq": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\Equity_history_raw.csv",
                                     cls.parsers),
            "fx": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\FX_history_raw.csv", cls.parsers),
            "ir": DataUtils.read_csv(r"C:\Users\naked\PycharmProjects\bh\resources\InterestRate_history_raw.csv",
                                     cls.parsers)
        }

    def test_read_csv(self):
        self.assertEqual(len(self.data_clean), 2)
        self.assertEqual(len(self.data_clean[self.hdr_date]), len(self.data_clean[self.hdr_last_price]))
        self.assertTrue(isinstance(self.data_clean[self.hdr_date][0], datetime.datetime))
        self.assertTrue(isinstance(self.data_clean[self.hdr_last_price][0], float))

    def test_parse_date(self):
        self.assertEqual(DataUtils.parse_date("11/12/2019"), datetime.datetime(2019, 12, 11))

    def test_parse_float(self):
        self.assertEqual(DataUtils.parse_float("5.6123"), 5.6123)

    def test_ewma(self):
        ewma = DataUtils.ew_ma(self.data_clean["eq"][self.hdr_last_price])
        self.assertEqual(len(ewma), len(self.data_clean["eq"][self.hdr_last_price]))
        self.assertAlmostEqual(ewma[-1], 5319.445113673711, delta=1e-14)

    def test_pct_change(self):
        pct = DataUtils.pct_change(self.data_clean["eq"][self.hdr_last_price])
        pass

    def test_ew_zsc(self):
        # ew_zsc = DataUtils.ew_zsc(pc)
        pass

    def test_stale_data(self):
        for k, v in self.data_raw.items():
            tr = TimeSeries(v[self.hdr_date], v[self.hdr_last_price])
            dr = DataUtils.stale_data(tr.prices, tr.dates, datetime.timedelta(weeks=1))
            print(str(k) + " raw " + str(len(dr)) + " " + str([tr.dates[i] for i, d in dr]) + " "
                  + str([tr.prices[i] for i, d in dr]))

        for k, v in self.data_clean.items():
            tc = TimeSeries(v[self.hdr_date], v[self.hdr_last_price])
            dc = DataUtils.stale_data(tc.prices, tc.dates, datetime.timedelta(weeks=1))
            print(str(k) + " clean " + str(len(dc)) + " " + str([tc.dates[i] for i, d in dc]) + " "
                  + str([tc.prices[i] for i, d in dc]))

    def test_ew_var(self):
        ew_var = DataUtils.ew_var(self.data_clean["eq"][self.hdr_last_price])
        # self.assertEqual(len(ew_var), len(self.data_clean[self.hdr_last_price]))
        # self.assertAlmostEqual(ew_var[-1], 5319.445113673711, delta=1e-14)

    def test_forward_fill_na(self):
        cleaned = DataUtils.forward_fill_na(self.data_raw[self.hdr_last_price])
        self.assertEqual(len([c for c in cleaned if c != c]), 0)
