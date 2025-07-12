def is_active_directory_account(username: str) -> bool:
    """
    Eğer username 'pam' ile başlıyorsa Active Directory hesabıdır.
    Aksi halde local hesap kabul edilir.
    """
    if not username:
        return False  # Boş veya None ise local olarak kabul edebiliriz

    return username.lower().startswith("pam")


def parse_applications(app_str: str) -> list:
    """
    Virgülle ayrılmış application stringini listeye çevirir.
    Her elemanı temizler (strip).
    """
    if not app_str:
        return []
    return [app.strip().upper() for app in app_str.split(",")]


def separate_managed_system_types(app_list: list) -> tuple:
    """
    application listesinden managed system tiplerini (sadece 'RDP' veya 'SSH')
    ve managed account'a bağlanacak diğer uygulamaları ayırır.
    Sistem tipi olarak en fazla 1 tip döner (ilk bulunan).
    """
    valid_system_types = {"RDP", "SSH"}
    system_type = None
    account_apps = []

    for app in app_list:
        if app in valid_system_types and system_type is None:
            system_type = app  # İlk RDP veya SSH tipi alınır
        else:
            account_apps.append(app)

    # system_type None ise boş liste, değilse liste olarak dönelim
    return ([system_type] if system_type else []), account_apps