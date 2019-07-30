import logging
from itertools import groupby
from unittest import TestCase

from src.data_cleaning import check_file_data
from definitions import CSV_PATHS, DataSource


class TestDataCleaning(TestCase):

    def test_data_cleaner(self):
        file_error_bounds = {
            DataSource.EQ_CLEAN: (0, 20),
            DataSource.FX_CLEAN: (0, 20),
            DataSource.IR_CLEAN: (0, 20),
            DataSource.EQ_RAW: (71, 1e6),
            DataSource.FX_RAW: (39, 1e6),
            DataSource.IR_RAW: (31, 1e6)
        }

        file_outliers = {}
        for name, file_path in CSV_PATHS.items():
            outliers = check_file_data(file_path)
            counts = {k: len(list(g)) for k, g in groupby(outliers, lambda x: x[2])}
            logging.info(name.name + "  Total: " + str(len(outliers)) + "  Breakdown: " + str(counts))
            file_outliers[name] = outliers

        for name, outliers in file_outliers.items():
            self.assertGreaterEqual(len(outliers), file_error_bounds[name][0])
            self.assertLessEqual(len(outliers), file_error_bounds[name][1])
