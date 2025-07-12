import os
import requests
from config.settings import API_URL

def get_all_managed_systems():
    session_id = os.getenv("ASP_NET_SESSION_ID")

    url = f"{API_URL}/ManagedSystems"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    return response.json()

def delete_managed_system_by_id(managed_system_id: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")

    url = f"{API_URL}/ManagedSystems/{managed_system_id}"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }
    response = requests.delete(url, headers=headers, verify=False)
    response.raise_for_status()
