import os

def get_auth_headers(token: str = None) -> dict:
    headers = {
        "Content-Type": "application/json"
    }
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if session_id:
        headers["Cookie"] = f"ASP.NET_SessionId={session_id}"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
