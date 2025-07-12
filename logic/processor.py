from excel.reader import read_excel_data
from utils.logger import log_message
from config.settings import *
from logic.validators import parse_applications, separate_managed_system_types


def process_row(row_index: int, row: dict):
    target_user = row.get('Target system user name')
    target_address = row.get('Target system address')
    application = row.get('Application')
    users = row.get('Erişecek Kullanıcılar')
    port = row.get('Port')
    db_name = row.get('DatabaseName')

    # Log mesajı
    message = (
        f"Row {row_index + 2}: "  # +2 çünkü 0 index + 1 header
        f"İşlem yapılıyor: "
        f"Managed Account -> {target_user} *** "
        f"Managed System -> {target_address} *** "
        f"Application -> {application} *** "
        f"Users -> {users} *** "
        f"Port -> {port} *** "
        f"Database -> {db_name}"
    )
    log_message(message)

    app_list = parse_applications(application)
    system_types, account_apps = separate_managed_system_types(app_list)

    print("Managed System tipleri:", system_types)  # ['SSH', 'WINSCP']
    print("Managed Account uygulamaları:", account_apps)  # ['SQL DEV']


def process_all_rows():
    df = read_excel_data(EXCEL_FILE_PATH)
    for index, row in df.iterrows():
        process_row(index, row.to_dict())