from excel.reader import read_excel_data
from utils.logger import log_message, log_error
from config.settings import EXCEL_FILE_PATH, DOMAIN_MANAGED_SYSTEM_ID
from logic.validators import parse_applications, separate_managed_system_types
from logic.network import resolve_target_address
from api.managed_system import ensure_managed_system_rdp, ensure_managed_system_ssh
from api.managed_account import (
    ensure_ad_managed_account,
    link_ad_account_to_managed_system,
    ensure_local_managed_account
)
from api.applications import assign_apps_to_account
from api.user_groups import ensure_user_groups_and_assign_smartrule

def process_row(row_index: int, row: dict):
    target_user = row.get('Target system user name')
    target_address = row.get('Target system address')
    application = row.get('Application')
    users = row.get('Erişecek Kullanıcılar')
    port = row.get('Port')
    db_name = row.get('DatabaseName')

    # IP ve DNS çözümleme
    resolved = resolve_target_address(target_address)
    target_ip = resolved.get("target_ip_address")
    target_dns = resolved.get("target_dns_name")

    if not target_ip:
        log_error(
            row_index + 2,
            "Hostname çözümlenemedi.",
            error_type="Network",
            hostname=target_address
        )
        log_message(f"Row {row_index + 2}: IP çözümlenemediği için işlem atlandı.")
        return

    log_message(
        f"Row {row_index + 2}: İşlem başlatıldı → Account='{target_user}', System='{target_address}', App='{application}', Users='{users}', Port='{port}', DB='{db_name}'"
    )

    app_list = parse_applications(application)
    system_types, account_apps = separate_managed_system_types(app_list)

    log_message(f"Row {row_index + 2}: Managed System tipleri: {system_types}")
    log_message(f"Row {row_index + 2}: Managed Account uygulamaları: {account_apps}")

    # Managed system oluşturulması
    if "RDP" in system_types:
        ensure_managed_system_rdp(target_ip, target_dns, target_user, row_index)
    elif "SSH" in system_types:
        ensure_managed_system_ssh(target_ip, target_dns, row_index)

    # Managed account işlemleri
    is_domain_account = target_user.lower().startswith("pam")

    if is_domain_account:
        ensure_ad_managed_account(target_user, row_index)
        link_ad_account_to_managed_system(target_user, target_ip, row_index, app_list)

        if account_apps:
            assign_apps_to_account(
                account_name=target_user,
                target_ip=target_ip,
                app_list=account_apps,
                is_domain=True,
                row_index=row_index,
                domain_system_id=DOMAIN_MANAGED_SYSTEM_ID
            )
    else:
        ensure_local_managed_account(target_user, target_ip, row_index, app_list=app_list)

        if account_apps:
            assign_apps_to_account(
                account_name=target_user,
                target_ip=target_ip,
                app_list=account_apps,
                is_domain=False,
                row_index=row_index,
                domain_system_id=None
            )

    # User Group işlemleri (sadece varsa)
    if users:
        users_list = [u.strip() for u in users.split(",") if u.strip()]
        ensure_user_groups_and_assign_smartrule(users_list, target_user, row_index, ip_address=target_ip)
def process_all_rows():
    df = read_excel_data(EXCEL_FILE_PATH)
    for index, row in df.iterrows():
        process_row(index, row.to_dict())
