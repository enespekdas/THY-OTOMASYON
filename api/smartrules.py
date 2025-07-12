import os
import requests
from config.settings import API_URL, SMART_RULE_PREFIX, DOMAIN_MANAGED_SYSTEM_ID
from utils.logger import log_message, log_error
from api.managed_system import get_all_managed_systems

def get_existing_smart_rules():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (smart rule listesi).", error_type="Session")
        return []

    url = f"{API_URL}/SmartRules"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(-1, f"SmartRule listesi alınamadı: {response.status_code} - {response.text}", error_type="SmartRuleList")
            return []
    except Exception as e:
        log_error(-1, f"SmartRule çekilirken hata: {str(e)}", error_type="SmartRuleList")
        return []

def smart_rule_exists(title: str) -> bool:
    rules = get_existing_smart_rules()
    return any(rule.get("Title") == title for rule in rules)

def create_smart_rule(account_name: str, ip_address: str, row_index: int):
    from api.managed_account import get_all_managed_accounts  # Döngüsel importu önlemek için fonksiyon içinde import

    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(row_index + 2, "Session ID bulunamadı (smart rule create).", error_type="SmartRule")
        return

    # Pam ile başlayan hesaplarda IP yok, diğerlerinde IP ile title oluştur
    if account_name.lower().startswith("pam"):
        title = f"{SMART_RULE_PREFIX}_{account_name}"
        system_id = DOMAIN_MANAGED_SYSTEM_ID
        description = f"This smart rule was created for {account_name}"
        ip_for_log = ""  # IP loglarda kullanmayabiliriz
    else:
        title = f"{SMART_RULE_PREFIX}_{account_name}_{ip_address}"
        systems = get_all_managed_systems()
        system = next((s for s in systems if str(s.get("IPAddress", "")).strip() == ip_address.strip()), None)
        if not system:
            log_error(row_index + 2, f"Managed System bulunamadı (SmartRule): {ip_address}", error_type="SmartRule")
            return
        system_id = system.get("ManagedSystemID")
        description = f"This smart rule was created for {ip_address} - {account_name}"
        ip_for_log = ip_address

    if smart_rule_exists(title):
        log_message(f"Row {row_index + 2}: SmartRule '{title}' zaten mevcut. Atlandı.")
        return

    accounts = get_all_managed_accounts(system_id)
    account = next((a for a in accounts if a.get("AccountName") == account_name), None)
    if not account:
        log_error(row_index + 2, f"Managed Account bulunamadı (SmartRule): {account_name}", error_type="SmartRule")
        return

    account_id = account.get("ManagedAccountID")

    payload = {
        "IDs": [account_id],
        "Title": title,
        "Category": "Quick Rules",
        "Description": description,
        "RuleType": "ManagedAccount"
    }

    url = f"{API_URL}/QuickRules"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            log_message(f"Row {row_index + 2}: SmartRule '{title}' başarıyla oluşturuldu.")
        else:
            log_error(row_index + 2, f"SmartRule oluşturulamadı: {response.status_code} - {response.text}", error_type="SmartRule")
    except Exception as e:
        log_error(row_index + 2, f"API hatası (SmartRule create): {str(e)}", error_type="SmartRule")
