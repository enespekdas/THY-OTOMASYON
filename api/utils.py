import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_session() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session
