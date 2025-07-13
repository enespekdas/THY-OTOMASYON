import os
import requests
import json
from config.settings import API_URL, LOCAL_GROUP_PERMISSION
from utils.logger import log_message, log_error

def get_session_id():
    session_id = os.getenv("ASP_NET_SESSION_ID")
    if not session_id:
        log_error(-1, "Session ID bulunamadı (user groups).", error_type="Session")
    return session_id

def get_all_user_groups():
    session_id = get_session_id()
    if not session_id:
        return []
    url = f"{API_URL}/UserGroups"
    headers = {"Cookie": f"ASP.NET_SessionId={session_id}"}
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            log_error(-1, f"UserGroups listesi alınamadı: {response.status_code} - {response.text}", error_type="UserGroupList")
            return []
    except Exception as e:
        log_error(-1, f"UserGroups API hatası: {str(e)}", error_type="UserGroupList")
        return []

def ensure_user_groups(users_list: list, row_index: int):
    existing_groups = get_all_user_groups()
    existing_names = [g.get("GroupName", "").upper() for g in existing_groups]

    try:
        permissions = json.loads(
            LOCAL_GROUP_PERMISSION.replace("PermissionID", "\"PermissionID\"").replace("AccessLevelID", "\"AccessLevelID\"")
        )
    except Exception as e:
        log_error(row_index + 2, f"LOCAL_GROUP_PERMISSION parse hatası: {str(e)}", error_type="UserGroupCreate")
        return

    for user in users_list:
        group_name = user.strip().upper()
        if group_name in existing_names:
            log_message(f"Row {row_index + 2}: User Group '{group_name}' zaten mevcut. Atlandı.")
            continue

        payload = {
            "groupType": "BeyondInsight",
            "groupName": group_name,
            "description": group_name,
            "isActive": True,
            "Permissions": permissions,
            "SmartRuleAccess": []  # Şimdilik boş, sonradan eklenecek
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
            else:
                error_text = response.text.lower()
                if "already exists" in error_text:
                    log_message(f"Row {row_index + 2}: User Group '{group_name}' zaten mevcut. Atlandı.")
                else:
                    log_error(row_index + 2, f"User Group oluşturulamadı: {response.status_code} - {response.text}", error_type="UserGroupCreate")
        except Exception as e:
            log_error(row_index + 2, f"User Group API hatası: {str(e)}", error_type="UserGroupCreate")
