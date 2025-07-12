import os
import requests
from config.settings import API_URL
from utils.logger import log_message, log_error
from api.managed_system import get_all_managed_systems
from api.managed_account import get_all_managed_accounts


def get_session_id():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (applications).", error_type="Session")
    return session_id


def get_all_applications():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/Applications"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(-1, f"Application listesi alınamadı: {response.status_code} - {response.text}", error_type="ApplicationList")
            return []
    except Exception as e:
        log_error(-1, f"Application listesi çekilirken hata: {str(e)}", error_type="ApplicationList")
        return []


def get_application_id_by_display_name(app_name: str):
    apps = get_all_applications()
    for app in apps:
        if app.get("DisplayName", "").strip().lower() == app_name.strip().lower():
            return app.get("ApplicationID")
    return None


def is_application_already_assigned(account_id: int, application_id: int) -> bool:
    session_id = get_session_id()
    if not session_id:
        return False

    url = f"{API_URL}/ManagedAccounts/{account_id}/Applications"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            assigned_apps = response.json()
            return any(app.get("ApplicationID") == application_id for app in assigned_apps)
        else:
            log_error(-1, f"Application kontrol hatası: {response.status_code} - {response.text}", error_type="ApplicationCheck")
            return False
    except Exception as e:
        log_error(-1, f"Application kontrol API hatası: {str(e)}", error_type="ApplicationCheck")
        return False


def assign_application_to_account(account_id: int, application_id: int, row_index: int):
    session_id = get_session_id()
    if not session_id:
        return

    if is_application_already_assigned(account_id, application_id):
        log_message(f"Row {row_index + 2}: ApplicationID {application_id} zaten atanmış. Atlandı.")
        return

    url = f"{API_URL}/ManagedAccounts/{account_id}/Applications/{application_id}"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}

    try:
        response = requests.post(url, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            log_message(f"Row {row_index + 2}: ApplicationID {application_id}, AccountID {account_id} hesabına başarıyla atandı.")
        else:
            log_error(row_index + 2, f"Application atama hatası: {response.status_code} - {response.text}", error_type="ApplicationAssign")
    except Exception as e:
        log_error(row_index + 2, f"Application atama API hatası: {str(e)}", error_type="ApplicationAssign")


def assign_apps_to_account(account_name: str, target_ip: str, app_list: list, is_domain: bool, row_index: int, domain_system_id: int):
    # 1. ManagedSystemID bul
    if is_domain:
        system_id = domain_system_id
    else:
        systems = get_all_managed_systems()
        system = next((s for s in systems if str(s.get("IPAddress", "")).strip() == target_ip.strip()), None)
        if not system:
            log_error(
                row_index + 2,
                f"Managed system bulunamadı (IP: {target_ip}).",
                error_type="ApplicationAssign",
                hostname=target_ip
            )
            return
        system_id = system.get("ManagedSystemID")

    # 2. ManagedAccountID bul
    accounts = get_all_managed_accounts(system_id)
    account = next((a for a in accounts if a.get("AccountName") == account_name), None)
    if not account:
        log_error(
            row_index + 2,
            f"Managed account bulunamadı: {account_name}",
            error_type="ApplicationAssign"
        )
        return

    account_id = account.get("ManagedAccountID")

    # 3. Her app için ID'yi bul ve atama yap
    for app_name in app_list:
        app_id = get_application_id_by_display_name(app_name)
        if not app_id:
            log_error(
                row_index + 2,
                f"Application bulunamadı: {app_name}",
                error_type="ApplicationAssign"
            )
            continue

        assign_application_to_account(account_id, app_id, row_index)
