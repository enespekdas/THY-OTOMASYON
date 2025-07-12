import os
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def _get_log_filename(prefix="import"):
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOG_DIR, f"{prefix}_{timestamp}.log")

# Global log dosyası isimleri
IMPORT_LOG_FILE = _get_log_filename("import")
ERROR_LOG_FILE = _get_log_filename("error")

def log_message(message: str):
    with open(IMPORT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def log_error(row_num: int, reason: str, error_type: str = "General", hostname: str = ""):
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        log_line = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
            f"Excel Row {row_num} -- [Error Type] = {error_type} -- "
            f"[Hostname] = {hostname} -- {reason}\n"
        )
        f.write(log_line)
