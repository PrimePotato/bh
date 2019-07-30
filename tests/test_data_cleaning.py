import logging
from itertools import groupby
from unittest import TestCase

from src.data_cleaning import check_file_data
from definitions import CSV_PATHS, DataSource


class TestDataCleaning(TestCase):

    def test_data_cleaner(self):
        file_error_bounds = {
            DataSource.EQ_CLEAN: lambda x: x < 20,
            DataSource.FX_CLEAN: lambda x: x < 20,
            DataSource.IR_CLEAN: lambda x: x < 20,
            DataSource.EQ_RAW: lambda x: x > 71,
            DataSource.FX_RAW: lambda x: x > 39,
            DataSource.IR_RAW: lambda x: x > 31,
        }

        file_outliers = {}
        for name, file_path in CSV_PATHS.items():
            outliers = check_file_data(file_path)
            outliers_dates = [d for d, v, o in outliers]
            self.assertEqual(len(outliers_dates), len(set(outliers_dates)))
            counts = {k: len(list(g)) for k, g in groupby(outliers, lambda x: x[2])}
            logging.info(name.name + "  Total: " + str(len(outliers)) + "  Breakdown: " + str(counts))
            file_outliers[name] = outliers

        for name, outliers in file_outliers.items():
            self.assertTrue(file_error_bounds[name](len(outliers)))
