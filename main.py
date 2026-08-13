"""
Enterprise AI Business Decision Intelligence
Main Entry Point
"""

from config.config import ROOT_DIR, DATASET_DIR, MODEL_DIR, OUTPUT_DIR, LOG_DIR
from config.logger import get_logger

logger = get_logger("EnterpriseAI")


def main():
    logger.info("Enterprise AI Project Started")

    print("=" * 60)
    print("Enterprise AI Business Decision Intelligence")
    print("=" * 60)

    print(f"Root Directory : {ROOT_DIR}")
    print(f"Dataset Folder : {DATASET_DIR}")
    print(f"Model Folder   : {MODEL_DIR}")
    print(f"Output Folder  : {OUTPUT_DIR}")
    print(f"Log Folder     : {LOG_DIR}")

    logger.info("Configuration loaded successfully.")


if __name__ == "__main__":
    main()