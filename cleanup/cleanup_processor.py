# cleanup/cleanup_processor.py

from excel.reader import read_excel_data
from config.settings import EXCEL_FILE_PATH
from logic.network import resolve_target_address
from cleanup.managed_system import get_all_managed_systems, delete_managed_system_by_id
from utils.logger import log_message

def cleanup_managed_systems_from_excel():
    df = read_excel_data(EXCEL_FILE_PATH)
    systems = get_all_managed_systems()
    
    for index, row in df.iterrows():
        target_address = row.get('Target system address')
        resolved = resolve_target_address(target_address)
        target_ip = resolved["target_ip_address"]

        if not target_ip:
            log_message(f"Row {index+2}: IP çözümlenemediği için silme atlandı.")
            continue

        match = next((s for s in systems if s.get("IPAddress") == target_ip), None)

        if match:
            ms_id = match.get("ManagedSystemID")
            delete_managed_system_by_id(ms_id)
            log_message(f"Row {index+2}: Managed System ID {ms_id} silindi. IP: {target_ip}")
        else:
            log_message(f"Row {index+2}: IP {target_ip} için eşleşen Managed System bulunamadı.")
