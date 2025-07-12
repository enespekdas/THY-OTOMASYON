import os
import requests
from config.settings import (
    API_URL,
    DOMAIN_MANAGED_SYSTEM_ID,
    DOMAIN_NAME,
    DEFAULT_AD_PASSWORD,
    WORKGROUP_ID
)
from utils.logger import log_message, log_error


def get_all_managed_accounts(managed_system_id: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (managed account listesi).", error_type="Session")
        return []

    url = f"{API_URL}/ManagedSystems/{managed_system_id}/ManagedAccounts"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(
                -1,
                f"Managed Account listesi alınamadı: {response.status_code} - {response.text}",
                error_type="AccountList"
            )
            return []
    except Exception as e:
        log_error(-1, f"API çağrısı sırasında hata (account list): {str(e)}", error_type="AccountList")
        return []


def create_ad_managed_account(account_name: str, row_index: int):
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(row_index + 2, "Session ID bulunamadı (create AD account).", error_type="Session")
        return

    url = f"{API_URL}/ManagedSystems/{DOMAIN_MANAGED_SYSTEM_ID}/ManagedAccounts"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "DomainName": DOMAIN_NAME,
        "AccountName": account_name,
        "DistinguishedName": None,
        "PasswordRuleID": 0,
        "Password": DEFAULT_AD_PASSWORD,
        "WorkgroupID": WORKGROUP_ID,
        "ObjectID": None,
        "UserPrincipalName": account_name,
        "SAMAccountName": account_name
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code == 201:
            log_message(f"Row {row_index + 2}: AD Managed Account '{account_name}' başarıyla oluşturuldu.")
        else:
            log_error(
                row_index + 2,
                f"AD Managed Account oluşturulamadı: {response.status_code} - {response.text}",
                error_type="Create"
            )
    except Exception as e:
        log_error(row_index + 2, f"AD Managed Account API hatası: {str(e)}", error_type="Create")


def ensure_ad_managed_account(account_name: str, row_index: int):
    accounts = get_all_managed_accounts(DOMAIN_MANAGED_SYSTEM_ID)
    exists = any(acct.get("AccountName") == account_name for acct in accounts)

    if exists:
        log_message(f"Row {row_index + 2}: AD Managed Account '{account_name}' zaten mevcut. Atlandı.")
    else:
        create_ad_managed_account(account_name, row_index)


def link_ad_account_to_managed_system(account_name: str, target_ip: str, row_index: int, app_list: list = None):
    from api.managed_system import get_all_managed_systems  # döngüsel importu önlemek için içeride import ettik

    if app_list is None:
        app_list = []

    # 1. Domain managed system'deki account'ları getir
    ad_accounts = get_all_managed_accounts(DOMAIN_MANAGED_SYSTEM_ID)
    ad_account = next((a for a in ad_accounts if a.get("AccountName") == account_name), None)

    if not ad_account:
        log_error(row_index + 2, f"'{account_name}' isimli AD account bulunamadı (linkleme iptal).", error_type="Linking", hostname=target_ip)
        return

    ad_account_id = ad_account.get("ManagedAccountID")

    # 2. Tüm managed system'leri getir, IP'ye göre bul
    systems = get_all_managed_systems()
    target_system = next((s for s in systems if str(s.get("IPAddress", "")).strip() == target_ip.strip()), None)

    if not target_system:
        # Burada uygulama listesini log mesajına ekliyoruz
        apps_str = ", ".join(app_list) if app_list else "Uygulama bilgisi yok"
        log_error(
            row_index + 2,
            f"IP '{target_ip}' için hedef managed system bulunamadı (linkleme iptal). Application Column List: {apps_str}",
            error_type="Linking",
            hostname=target_ip
        )
        return

    target_system_id = target_system.get("ManagedSystemID")

    # 3. Linkleme isteği gönder
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(row_index + 2, "Session ID bulunamadı (linkleme işlemi).", error_type="Linking", hostname=target_ip)
        return

    url = f"{API_URL}/ManagedSystems/{target_system_id}/LinkedAccounts/{ad_account_id}"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, headers=headers, verify=False)
        if response.status_code in [200, 201]:  # Başarı durumları
            log_message(f"Row {row_index + 2}: AD hesabı '{account_name}' → IP {target_ip} sistemine başarıyla linklendi.")
        elif response.status_code == 409:
            log_message(f"Row {row_index + 2}: AD hesabı '{account_name}' zaten linkli. Atlandı.")
        else:
            log_error(
                row_index + 2,
                f"Linkleme hatası: {response.status_code} - {response.text}",
                error_type="Linking",
                hostname=target_ip
            )
    except Exception as e:
        log_error(row_index + 2, f"API hatası (linkleme): {str(e)}", error_type="Linking", hostname=target_ip)