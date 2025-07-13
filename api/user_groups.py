import os
import requests
import json
from config.settings import (
    API_URL,
    LOCAL_GROUP_PERMISSION,
    SMART_RULE_PREFIX,
    ACCESS_POLICY_ID,
    FOREST_NAME,
    DOMAIN_NAME,
    BIND_USER,
    BIND_PASSWORD
)
from utils.logger import log_message, log_error

def get_session_id():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (user groups).", error_type="Session")
    else:
        log_message(f"Session ID bulundu: {session_id[:8]}...")
    return session_id

def get_all_user_groups():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/UserGroups"
    headers = { "Cookie": f"ASP.NET_SessionId={session_id}" }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            log_message("UserGroups listesi başarıyla alındı.")
            return response.json()
        else:
            log_error(-1, f"UserGroups alınamadı: {response.status_code} - {response.text}", error_type="UserGroupList")
            return []
    except Exception as e:
        log_error(-1, f"UserGroups API hatası: {str(e)}", error_type="UserGroupList")
        return []

def get_all_smartrules():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/SmartRules"
    headers = { "Cookie": f"ASP.NET_SessionId={session_id}" }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            log_message("SmartRules listesi başarıyla alındı.")
            return response.json()
        else:
            log_error(-1, f"SmartRules alınamadı: {response.status_code} - {response.text}", error_type="SmartRuleList")
            return []
    except Exception as e:
        log_error(-1, f"SmartRules API hatası: {str(e)}", error_type="SmartRuleList")
        return []

def find_smartrule_id(account_name: str, ip_address: str = None):
    smart_rules = get_all_smartrules()
    if account_name.lower().startswith("pam"):
        expected_name = f"{SMART_RULE_PREFIX}_pam{account_name[3:].lower()}"
    else:
        if not ip_address:
            log_message(f"Local hesap için IP eksik: {account_name}")
            return None
        expected_name = f"{SMART_RULE_PREFIX}_{account_name.lower()}_{ip_address}"

    for rule in smart_rules:
        if rule.get("Title", "").lower() == expected_name.lower():
            log_message(f"SmartRule bulundu: {expected_name} (ID: {rule['SmartRuleID']})")
            return rule["SmartRuleID"]

    log_message(f"SmartRule bulunamadı: {expected_name}")
    return None

def assign_smartrule_to_group(group_id: int, smart_rule_id: int, access_level_id: int, row_index: int) -> bool:
    session_id = get_session_id()
    if not session_id:
        return False

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    url = f"{API_URL}/UserGroups/{group_id}/SmartRules/{smart_rule_id}/AccessLevels"
    payload = { "AccessLevelID": access_level_id }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            log_message(f"Row {row_index + 2}: SmartRule (ID: {smart_rule_id}) başarıyla group'a atandı.")

            # Role + AccessPolicy atama
            role_url = f"{API_URL}/UserGroups/{group_id}/SmartRules/{smart_rule_id}/Roles"
            role_payload = {
                "Roles": [{ "RoleID": "3" }],
                "AccessPolicyID": ACCESS_POLICY_ID
            }
            role_resp = requests.post(role_url, json=role_payload, headers=headers, verify=False)
            if role_resp.status_code in [200, 204]:
                log_message(f"Row {row_index + 2}: Role ve AccessPolicy başarıyla atandı.")
            else:
                log_error(row_index + 2, f"Role ataması başarısız: {role_resp.status_code} - {role_resp.text}", error_type="SmartRuleRoleAssign")
            return True
        else:
            log_error(row_index + 2, f"SmartRule atama hatası: {response.status_code} - {response.text}", error_type="SmartRuleAssign")
            return False
    except Exception as e:
        log_error(row_index + 2, f"SmartRule atama API hatası: {str(e)}", error_type="SmartRuleAssign")
        return False

def get_all_users():
    session_id = get_session_id()
    if not session_id:
        return []

    url = f"{API_URL}/Users"
    headers = { "Cookie": f"ASP.NET_SessionId={session_id}" }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(-1, f"Users alınamadı: {response.status_code} - {response.text}", error_type="UserList")
            return []
    except Exception as e:
        log_error(-1, f"Users API hatası: {str(e)}", error_type="UserList")
        return []

def create_user(user_name: str, row_index: int):
    session_id = get_session_id()
    if not session_id:
        return

    url = f"{API_URL}/Users/"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "UserType": "ActiveDirectory",
        "UserName": user_name,
        "ForestName": FOREST_NAME,
        "DomainName": DOMAIN_NAME,
        "BindUser": BIND_USER,
        "BindPassword": BIND_PASSWORD,
        "UseSSL": "false"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code in [200, 201]:
            log_message(f"Row {row_index + 2}: Kullanıcı '{user_name}' başarıyla oluşturuldu.")
        else:
            log_error(row_index + 2, f"Kullanıcı oluşturulamadı: {response.status_code} - {response.text}", error_type="UserCreate")
    except Exception as e:
        log_error(row_index + 2, f"Kullanıcı oluşturma API hatası: {str(e)}", error_type="UserCreate")

def add_user_to_group(group_id: int, user_name: str, row_index: int):
    session_id = get_session_id()
    if not session_id:
        return

    # Önce user listesi çekilip user_id alınmalı
    users = get_all_users()
    user = next((u for u in users if u.get("UserName", "").upper() == user_name.upper()), None)

    if not user:
        log_error(row_index + 2, f"Kullanıcı bulunamadı: {user_name}", error_type="UserGroupMembership")
        return

    user_id = user.get("UserID")
    if not user_id:
        log_error(row_index + 2, f"UserID alınamadı: {user_name}", error_type="UserGroupMembership")
        return

    url = f"{API_URL}/Users/{user_id}/UserGroups/{group_id}"
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"ASP.NET_SessionId={session_id}"
    }

    payload = {
        "GroupID": group_id,
        "Name": user_name,
        "DistinguishedName": "",  # AD grubu değil, kullanıcı; boş bırakılabilir
        "GroupType": "BeyondInsight",  # veya "ActiveDirectory" olabilir
        "AccountAttribute": "",
        "MembershipAttribute": "",
        "IsActive": True
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        if response.status_code in [200, 201, 204]:
            log_message(f"Row {row_index + 2}: Kullanıcı '{user_name}' başarıyla gruba eklendi (GroupID: {group_id}).")
        else:
            log_error(row_index + 2, f"Group üyeliği hatası: {response.status_code} - {response.text}", error_type="UserGroupMembership")
    except Exception as e:
        log_error(row_index + 2, f"Group üyeliği API hatası: {str(e)}", error_type="UserGroupMembership")


def ensure_user_groups_and_assign_smartrule(user_list: list, account_name: str, row_index: int, ip_address: str = None):
    log_message(f"Row {row_index + 2}: Group kontrol ve atama başlatıldı. Toplam kullanıcı: {len(user_list)}")

    existing_groups = get_all_user_groups()
    existing_users = get_all_users()

    try:
        permissions = json.loads(
            LOCAL_GROUP_PERMISSION.replace("PermissionID", "\"PermissionID\"").replace("AccessLevelID", "\"AccessLevelID\"")
        )
    except Exception as e:
        log_error(row_index + 2, f"LOCAL_GROUP_PERMISSION JSON parse hatası: {str(e)}", error_type="UserGroupCreate")
        return

    for user in user_list:
        group_name = user.strip().upper()
        group = next((g for g in existing_groups if g.get("Name", "").upper() == group_name), None)

        if not group:
            session_id = get_session_id()
            if not session_id:
                return

            url = f"{API_URL}/UserGroups"
            headers = {
                "Content-Type": "application/json",
                "Cookie": f"ASP.NET_SessionId={session_id}"
            }

            payload = {
                "groupType": "BeyondInsight",
                "groupName": group_name,
                "description": f"Auto created group for {group_name}",
                "isActive": True,
                "Permissions": permissions,
                "SmartRuleAccess": []
            }

            try:
                response = requests.post(url, json=payload, headers=headers, verify=False)
                if response.status_code in [200, 201]:
                    log_message(f"Row {row_index + 2}: Group oluşturuldu: {group_name}")
                    group = response.json()
                    existing_groups.append(group)
                else:
                    log_error(row_index + 2, f"Group oluşturulamadı: {response.status_code} - {response.text}", error_type="UserGroupCreate")
                    continue
            except Exception as e:
                log_error(row_index + 2, f"Group API hatası: {str(e)}", error_type="UserGroupCreate")
                continue

        group_id = group.get("GroupID")
        if not group_id:
            log_error(row_index + 2, f"Group ID bulunamadı: {group_name}", error_type="UserGroupCreate")
            continue

        smart_rule_id = find_smartrule_id(account_name, ip_address)
        if not smart_rule_id:
            log_message(f"Row {row_index + 2}: SmartRule bulunamadı: {account_name}")
            continue

        success = assign_smartrule_to_group(group_id, smart_rule_id, access_level_id=3, row_index=row_index)
        if not success:
            continue

        # User oluşturulmamışsa oluştur
        if not any(u.get("UserName", "").upper() == group_name for u in existing_users):
            create_user(group_name, row_index)

        # Kullanıcıyı gruba ekle
        add_user_to_group(group_id, group_name, row_index)
