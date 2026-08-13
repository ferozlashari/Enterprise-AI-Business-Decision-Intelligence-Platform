"""
Enterprise AI Configuration
"""

from pathlib import Path

# ==========================
# Project Root
# ==========================

ROOT_DIR = Path(__file__).resolve().parent.parent

# ==========================
# Folders
# ==========================

DATASET_DIR = ROOT_DIR / "datasets"

MODEL_DIR = ROOT_DIR / "saved_models"

OUTPUT_DIR = ROOT_DIR / "outputs"

LOG_DIR = ROOT_DIR / "logs"

# ==========================
# Create folders automatically
# ==========================

MODEL_DIR.mkdir(exist_ok=True)

OUTPUT_DIR.mkdir(exist_ok=True)

LOG_DIR.mkdir(exist_ok=True)

# ==========================
# Dataset Paths
# ==========================

CUSTOMER_DATA = DATASET_DIR / "customers.csv"

SUPERSTORE_DATA = DATASET_DIR / "superstore.csv"

STORE_SALES_DIR = DATASET_DIR / "store_sales"

TRAIN_DATA = STORE_SALES_DIR / "train.csv"

STORES_DATA = STORE_SALES_DIR / "stores.csv"

TRANSACTION_DATA = STORE_SALES_DIR / "transactions.csv"

OIL_DATA = STORE_SALES_DIR / "oil.csv"