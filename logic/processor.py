from excel.reader import read_excel_data
from utils.logger import log_message, log_error
from config.settings import EXCEL_FILE_PATH
from logic.validators import parse_applications, separate_managed_system_types
from logic.network import resolve_target_address
from api.managed_system import ensure_managed_system_rdp, ensure_managed_system_ssh
from api.managed_account import ensure_ad_managed_account, link_ad_account_to_managed_system,ensure_local_managed_account


def process_row(row_index: int, row: dict):
    target_user = row.get('Target system user name')
    target_address = row.get('Target system address')
    application = row.get('Application')
    users = row.get('Erişecek Kullanıcılar')
    port = row.get('Port')
    db_name = row.get('DatabaseName')

    ### Ip ve dns adresleri bulunuyor.
    resolved = resolve_target_address(target_address)
    target_ip = resolved.get("target_ip_address")
    target_dns = resolved.get("target_dns_name")

    if not target_ip:
        log_error(row_index + 2, "Hostname çözümlenemedi.", error_type="Network", hostname=target_address)
        log_message(f"Row {row_index + 2}: Excel Satır: IP çözümlenemediği için işlem atlandı.")
        return

    message = f"Row {row_index + 2}: İşlem: Account={target_user} | System={target_address} | App={application} | Users={users} | Port={port} | DB={db_name}"
    log_message(message)

    app_list = parse_applications(application)
    system_types, account_apps = separate_managed_system_types(app_list)

    print("Managed System tipleri:", system_types)
    print("Managed Account uygulamaları:", account_apps)

    ### managed systemler ekleniyor.
    if "RDP" in system_types:
        ensure_managed_system_rdp(target_ip, target_dns, target_user, row_index)
    elif "SSH" in system_types:
        ensure_managed_system_ssh(target_ip, target_dns, row_index)

    if target_user.lower().startswith("pam"):
        ensure_ad_managed_account(target_user, row_index)
        # link_ad_account_to_managed_system fonksiyonuna uygulama listesini de gönderiyoruz
        link_ad_account_to_managed_system(target_user, target_ip, row_index, app_list)
    else:
        ensure_local_managed_account(target_user, target_ip, row_index, app_list=app_list)

def process_all_rows():
    df = read_excel_data(EXCEL_FILE_PATH)
    for index, row in df.iterrows():
        process_row(index, row.to_dict())
