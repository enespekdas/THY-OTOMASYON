import os
import requests
import json
from config.settings import API_URL, LOCAL_GROUP_PERMISSION, SMART_RULE_PREFIX,ACCESS_POLICY_ID
from utils.logger import log_message, log_error

def get_session_id():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (user groups).", error_type="Session")
    else:
        log_message(f"Session ID bulundu: {session_id[:8]}...")  # Güvenlik için tamamını yazma
    return session_id

def get_all_user_groups():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/UserGroups"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            log_message("UserGroups listesi başarıyla alındı.")
            return response.json()
        else:
            log_error(-1, f"UserGroups listesi alınamadı: {response.status_code} - {response.text}", error_type="UserGroupList")
            return []
    except Exception as e:
        log_error(-1, f"UserGroups API hatası: {str(e)}", error_type="UserGroupList")
        return []

def get_all_smartrules():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/SmartRules"
    headers = {
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            log_message("SmartRules listesi başarıyla alındı.")
            return response.json()
        else:
            log_error(-1, f"SmartRules listesi alınamadı: {response.status_code} - {response.text}", error_type="SmartRuleList")
            return []
    except Exception as e:
        log_error(-1, f"SmartRules API hatası: {str(e)}", error_type="SmartRuleList")
        return []

def find_smartrule_id(account_name: str, ip_address: str = None):
    """
    account_name: örn 'pam_user1' veya 'localuser_ipaddress' gibi isimlendirilmiş hesap.
    ip_address: local hesaplar için IP adresi verilmeli (örn: '192.168.10.34')
    """
    smart_rules = get_all_smartrules()

    if account_name.lower().startswith("pam"):
        expected_name = f"{SMART_RULE_PREFIX}_pam{account_name[3:].lower()}"
    else:
        if not ip_address:
            log_message(f"Local hesap için IP adresi sağlanmadı: {account_name}")
            return None
        expected_name = f"{SMART_RULE_PREFIX}_{account_name.lower()}_{ip_address}"

    for rule in smart_rules:
        if "Title" in rule and rule["Title"].lower() == expected_name.lower():
            log_message(f"SmartRule bulundu: {expected_name} (ID: {rule['SmartRuleID']})")
            return rule.get("SmartRuleID")

    log_message(f"SmartRule bulunamadı: {expected_name}")
    return None

def assign_smartrule_to_group(group_id: int, smart_rule_id: int, access_level_id: int, row_index: int):
    session_id = get_session_id()
    if not session_id:
        return False

    url = f"{API_URL}/UserGroups/{group_id}/SmartRules/{smart_rule_id}/AccessLevels"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }
    payload = {
        "AccessLevelID": access_level_id
    }
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            log_message(f"Row {row_index + 2}: SmartRule (ID: {smart_rule_id}) başarıyla UserGroup (ID: {group_id})'a yetkilendirildi.")

            # --- Yeni Eklenen Adım: Role ve AccessPolicy Atama ---
            role_url = f"{API_URL}/UserGroups/{group_id}/SmartRules/{smart_rule_id}/Roles"
            role_payload = {
                "Roles": [{"RoleID": "3"}],
                "AccessPolicyID": ACCESS_POLICY_ID
            }

            role_response = requests.post(role_url, json=role_payload, headers=headers, verify=False)
            if role_response.status_code in [200, 204]:
                log_message(f"Row {row_index + 2}: Role ve AccessPolicy başarıyla atandı → GroupID: {group_id}, SmartRuleID: {smart_rule_id}")
            else:
                log_error(row_index + 2, f"Role ataması başarısız: {role_response.status_code} - {role_response.text}", error_type="SmartRuleRoleAssign")

            return True
        else:
            log_error(row_index + 2, f"SmartRule yetkilendirme başarısız: {response.status_code} - {response.text}", error_type="SmartRuleAssign")
            return False
    except Exception as e:
        log_error(row_index + 2, f"SmartRule yetkilendirme API hatası: {str(e)}", error_type="SmartRuleAssign")
        return False

def ensure_user_groups_and_assign_smartrule(user_list: list, account_name: str, row_index: int, ip_address: str = None):
    """
    user_list: Grup adı olacak kullanıcı listesi (ör: ['S_OZCAN', 'Y_UCUNCUOGLU'])
    account_name: SmartRule için kullanılacak hesap adı
    ip_address: local hesaplar için IP adresi (örn: '192.168.10.34')
    """
    log_message(f"Row {row_index + 2}: ensure_user_groups_and_assign_smartrule fonksiyonu çağrıldı, user sayısı: {len(user_list)}")

    existing_groups = get_all_user_groups()

    try:
        permissions = json.loads(
            LOCAL_GROUP_PERMISSION.replace("PermissionID", "\"PermissionID\"").replace("AccessLevelID", "\"AccessLevelID\"")
        )
    except Exception as e:
        log_error(row_index + 2, f"LOCAL_GROUP_PERMISSION parse hatası: {str(e)}", error_type="UserGroupCreate")
        return

    for user in user_list:
        group_name = user.strip().upper()
        log_message(f"Row {row_index + 2}: İşlem yapılan user/group: {group_name}")

        group = next((g for g in existing_groups if g.get("Name", "").upper() == group_name), None)
        if not group:
            payload = {
                "groupType": "BeyondInsight",
                "groupName": group_name,
                "description": f"Auto created group for {group_name}",
                "isActive": True,
                "Permissions": permissions,
                "SmartRuleAccess": []
            }

            session_id = get_session_id()
            if not session_id:
                return

            url = f"{API_URL}/UserGroups"
            headers = {
                "Content-Type": "application/json",
                "Cookie": f"ASP.NET_SessionId={session_id}"
            }

            try:
                response = requests.post(url, json=payload, headers=headers, verify=False)
                if response.status_code in [200, 201]:
                    log_message(f"Row {row_index + 2}: User Group '{group_name}' başarıyla oluşturuldu.")
                    group = response.json()
                    existing_groups.append(group)
                else:
                    if "already exists" in response.text.lower():
                        log_message(f"Row {row_index + 2}: User Group '{group_name}' zaten mevcut. Atlandı.")
                        group = next((g for g in existing_groups if g.get("Name", "").upper() == group_name), None)
                    else:
                        log_error(row_index + 2, f"User Group oluşturulamadı: {response.status_code} - {response.text}", error_type="UserGroupCreate")
                        continue
            except Exception as e:
                log_error(row_index + 2, f"User Group API hatası: {str(e)}", error_type="UserGroupCreate")
                continue

        if not group:
            log_error(row_index + 2, f"User Group '{group_name}' bulunamadı ve oluşturulamadı, SmartRule ataması yapılmadı.", error_type="UserGroupCreate")
            continue

        group_id = group.get("GroupID")
        if not group_id:
            log_error(row_index + 2, f"User Group ID bulunamadı: '{group_name}'", error_type="UserGroupCreate")
            continue

        smart_rule_id = find_smartrule_id(account_name, ip_address)
        if not smart_rule_id:
            log_message(f"Row {row_index + 2}: SmartRule bulunamadı, atlama: {account_name}")
            continue

        access_level_id = 3

        assign_smartrule_to_group(group_id, smart_rule_id, access_level_id, row_index)