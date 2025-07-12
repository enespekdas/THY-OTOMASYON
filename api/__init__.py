from .auth import sign_app_in
import os
import sys

token = None

def init_auth():
    global token
    token = sign_app_in()
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if session_id:
        print(f"Authentication başarılı.")
    else:
        print("Authentication başarısız! Session ID bulunamadı.")
        sys.exit(1)  # Programı durdurabiliriz veya hata fırlatabiliriz

init_auth()
