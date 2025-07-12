# api/managed_system.py

import os
import requests
from config.settings import API_URL, WINDOWS_MANAGED_SYSTEM_TEMPLATE ,WORKGROUP_ID
from utils.logger import log_message, log_error

def create_managed_system_rdp(target_ip: str, target_dns: str, target_user: str, row_index: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(row_index, "Session ID bulunamadı.")
        return

    url = f"{API_URL}/Workgroups/{WORKGROUP_ID}/ManagedSystems"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = WINDOWS_MANAGED_SYSTEM_TEMPLATE.copy()
    payload["HostName"] = target_ip
    payload["DnsName"] = target_dns
    payload["IPAddress"] = target_ip

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 201:
            log_message(f"{row_index + 2}. satır için RDP Managed System başarıyla oluşturuldu.")
        else:
            log_error(row_index, f"Managed System oluşturulamadı: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(row_index, f"API çağrısı sırasında hata: {str(e)}")
