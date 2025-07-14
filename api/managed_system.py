import os
import requests
import jmespath
from functools import lru_cache
from config.settings import (
    API_URL,
    WINDOWS_MANAGED_SYSTEM_TEMPLATE,
    LINUX_MANAGED_SYSTEM_TEMPLATE,
    WORKGROUP_ID,
)
from utils.logger import log_message, log_error


@lru_cache(maxsize=1)
def get_all_managed_systems():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (managed system listesi).")
        return []

    url = f"{API_URL}/ManagedSystems"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(-1, f"Managed system listesi alınamadı: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        log_error(-1, f"API çağrısı sırasında hata: {str(e)}")
        return []


def _find_managed_system_by_ip(systems, target_ip):
    # jmespath ile IP eşleşen kaydı buluyoruz, boş liste dönerse None olur
    expression = jmespath.compile(f"[?IPAddress == '{target_ip}'] | [0]")
    return expression.search(systems)


def create_managed_system_rdp(target_ip: str, target_dns: str, target_user: str, row_index: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(f"Row {row_index + 2}. Session ID bulunamadı.")
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
            log_message(f"Row {row_index + 2}. için RDP Managed System başarıyla oluşturuldu.")
            # Cache'i temizle ki yeni sistem görünsün
            get_all_managed_systems.cache_clear()
        else:
            log_error(f"Row {row_index + 2}. Managed System oluşturulamadı: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(f"Row {row_index + 2}. API çağrısı sırasında hata: {str(e)}")


def ensure_managed_system_rdp(target_ip: str, target_dns: str, target_user: str, row_index: int):
    systems = get_all_managed_systems()
    normalized_target_ip = target_ip.strip() if target_ip else ""

    match = _find_managed_system_by_ip(systems, normalized_target_ip)

    if match:
        log_message(f"Row {row_index + 2}: IP {normalized_target_ip} zaten managed system olarak mevcut. Atlandı.")
    else:
        create_managed_system_rdp(target_ip, target_dns, target_user, row_index)
        log_message(f"Row {row_index + 2}: IP {normalized_target_ip} için yeni RDP managed system oluşturuldu.")


# ✅ LINUX tarafı başlıyor

def create_managed_system_ssh(target_ip: str, target_dns: str, row_index: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(f"Row {row_index + 2}. Session ID bulunamadı.")
        return

    url = f"{API_URL}/Workgroups/{WORKGROUP_ID}/ManagedSystems"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = LINUX_MANAGED_SYSTEM_TEMPLATE.copy()
    payload["HostName"] = target_ip
    payload["DnsName"] = target_dns
    payload["IPAddress"] = target_ip
    payload["SystemName"] = target_ip  # Ekstra fark burada

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 201:
            log_message(f"Row {row_index + 2}: SSH Managed System başarıyla oluşturuldu.")
            get_all_managed_systems.cache_clear()
        else:
            log_error(f"Row {row_index + 2}: SSH Managed System oluşturulamadı: {response.status_code} - {response.text}")
    except Exception as e:
        log_error(f"Row {row_index + 2}: SSH API çağrısı sırasında hata: {str(e)}")


def ensure_managed_system_ssh(target_ip: str, target_dns: str, row_index: int):
    systems = get_all_managed_systems()
    normalized_target_ip = target_ip.strip() if target_ip else ""

    match = _find_managed_system_by_ip(systems, normalized_target_ip)

    if match:
        log_message(f"Row {row_index + 2}: IP {normalized_target_ip} zaten SSH managed system olarak mevcut. Atlandı.")
    else:
        create_managed_system_ssh(target_ip, target_dns, row_index)
        log_message(f"Row {row_index + 2}: IP {normalized_target_ip} için yeni SSH managed system oluşturuldu.")
