import requests

class BtpsClient:
    def __init__(self, base_url, auth_key, runas_user):
        self.base_url = base_url
        self.auth_key = auth_key
        self.runas_user = runas_user
        self.session = requests.Session()
        self.token = None

    def login(self):
        url = f"{self.base_url}/Auth/SignAppin"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"PS-Auth key={self.auth_key}; runas={self.runas_user};"
        }
        resp = self.session.post(url, headers=headers, verify=False)
        resp.raise_for_status()
        data = resp.json()
        self.token = data.get("Token")  # Token varsa kaydet
        # Cookie otomatik olarak self.session’da tutulur

    def get_users(self):
        url = f"{self.base_url}/Users"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        resp = self.session.get(url, headers=headers, verify=False)
        resp.raise_for_status()
        return resp.json()


# Kullanım
if __name__ == "__main__":
    client = BtpsClient(
        base_url="https://bt.quasys.local/BeyondTrust/api/public/v3",
        auth_key="043f1686e106b3f64c0fcb07b1a66168f09675aa74d7f6999c6109e2628ffe734cc0e26a7c476d6ee217713ff168beabb9f8438bd31637a75f96fd7bd0350ce1",
        runas_user="btadmin"
    )
    client.login()
    users = client.get_users()
    print(users)
