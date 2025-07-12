from excel.reader import read_excel_data
from utils.logger import log_message,log_error
from config.settings import *
from logic.validators import parse_applications, separate_managed_system_types

from logic.network import resolve_target_address
from api.managed_system import create_managed_system_rdp

def process_row(row_index: int, row: dict):
    target_user = row.get('Target system user name')
    target_address = row.get('Target system address')
    application = row.get('Application')
    users = row.get('Erişecek Kullanıcılar')
    port = row.get('Port')
    db_name = row.get('DatabaseName')

    # IP ve DNS isimlerini çöz
    resolved = resolve_target_address(target_address)
    target_ip = resolved["target_ip_address"]
    target_dns = resolved["target_dns_name"]

    if not target_ip:
        log_error(row_index, "Hostname çözümlenemedi.", error_type="Network", hostname=target_address)
        log_message(f"{row_index}. Excel Satir: IP çözümlenemediği için işlem atlandı.")
        return

        # Log mesajı
    message = f"Row {row_index + 2}: İşlem yapılıyor: Managed Account -> {target_user} *** Managed System -> {target_address} *** Application -> {application} *** Users -> {users} *** Port -> {port} *** Database -> {db_name}"
    log_message(message)


    app_list = parse_applications(application)
    system_types, account_apps = separate_managed_system_types(app_list)

    print("Managed System tipleri:", system_types)  # ['SSH', 'RDP']
    print("Managed Account uygulamaları:", account_apps)  # ['SQL DEV']
    if "RDP" in system_types:
        create_managed_system_rdp(target_ip, target_dns, target_user, row_index)

def process_all_rows():
    df = read_excel_data(EXCEL_FILE_PATH)
    for index, row in df.iterrows():
        process_row(index, row.to_dict())
        