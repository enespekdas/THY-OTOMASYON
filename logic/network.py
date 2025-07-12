import socket
import re
from typing import Optional

def resolve_ip_to_hostname(ip_address: str) -> Optional[str]:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.herror:
        return None

def resolve_hostname_to_ip(hostname: str) -> Optional[str]:
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None



def is_ip(address: str) -> bool:
    # Basit IP kontrolü (IPv4)
    pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    return bool(re.match(pattern, address))

def resolve_target_address(target_address: str) -> dict:
    """
    Gelen target_address hem IP hem hostname olabilir.
    Fonksiyon:
      - Eğer IP ise hostname'i bulur
      - Eğer hostname ise IP'sini bulur
    Dönüş: {'target_ip_address': ..., 'target_dns_name': ...}
    """
    if is_ip(target_address):
        ip = target_address
        dns = resolve_ip_to_hostname(ip)
    else:
        dns = target_address
        ip = resolve_hostname_to_ip(dns)
    return {
        "target_ip_address": ip,
        "target_dns_name": dns
    }