import os
from datetime import datetime

# Log klasörü ve dinamik dosya adı
LOG_DIR = "logs"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"import_{timestamp}.log")

# Klasör yoksa oluştur
os.makedirs(LOG_DIR, exist_ok=True)

def log_message(message: str):
    """
    Verilen mesajı log dosyasına timestamp ile yazar.
    """
    log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{log_timestamp}] {message}\n")
