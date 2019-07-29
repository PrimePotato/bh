import os
from enum import Enum, auto

import logging

logging.basicConfig(level=logging.INFO)


class DataSource(Enum):
    EQ_RAW = auto()
    EQ_CLEAN = auto()
    IR_RAW = auto()
    IR_CLEAN = auto()
    FX_RAW = auto()
    FX_CLEAN = auto()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATHS = {
    DataSource.EQ_CLEAN: os.path.join(ROOT_DIR, "resources", "Equity_history_clean.csv"),
    DataSource.FX_CLEAN: os.path.join(ROOT_DIR, "resources", "FX_history_clean.csv"),
    DataSource.IR_CLEAN: os.path.join(ROOT_DIR, "resources", "InterestRate_history_clean.csv"),
    DataSource.EQ_RAW: os.path.join(ROOT_DIR, "resources", "Equity_history_raw.csv"),
    DataSource.FX_RAW: os.path.join(ROOT_DIR, "resources", "FX_history_raw.csv"),
    DataSource.IR_RAW: os.path.join(ROOT_DIR, "resources", "InterestRate_history_raw.csv")
}
