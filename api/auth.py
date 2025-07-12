import os
from config import settings
from api.utils import get_session
from typing import Optional

session = get_session()

def sign_app_in() -> Optional[str]:
    """
    Login yapar, session cookie'yi ortam değişkenine set eder.
    Token varsa döner, yoksa None.
    """
    url = f"{settings.API_URL}/Auth/SignAppin"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"PS-Auth key={settings.AUTH_KEY}; runas={settings.RUNAS_USER};"
    }
    try:
        response = session.post(url, headers=headers)
        response.raise_for_status()

        aspnet_sessionid = response.cookies.get("ASP.NET_SessionId")
        if aspnet_sessionid:
            os.environ["ASP_NET_SESSION_ID"] = aspnet_sessionid
            #print(f"ASP.NET_SessionId environment variable set: {aspnet_sessionid}")
        else:
            print("Warning: ASP.NET_SessionId cookie not found!")

        token = response.json().get("Token")

        return token

    except Exception as exc:
        print(f"Authentication failed: {exc}")
        return None
