def process_row(row: dict):
    """
    Excel'den gelen tek bir satırı alır, iş kurallarına göre API çağrıları yapar.
    """
    target_user = row.get('Target system user name')
    target_address = row.get('Target system address')
    application = row.get('Application')
    users = row.get('Erişecek Kullanıcılar')
    port = row.get('Port')
    db_name = row.get('DatabaseName')

    # Buraya iş mantığını koyacağız, örnek:
    print(f"Processing {target_address} for user {target_user} with application {application}")
    # Örnek: Windows platform mu Linux mu kontrol et, ona göre managed system ekle
    # Sonra managed account ekle, application linkle vs.
