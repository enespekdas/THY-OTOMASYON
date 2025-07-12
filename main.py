import sys
import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(BASE_DIR)
from cleanup.cleanup_processor import cleanup_managed_systems_from_excel

from logic.processor import process_all_rows

if __name__ == "__main__":
    process_all_rows()

    #cleanup_managed_systems_from_excel()
