# config/settings.py

API_URL = "https://bt.quasys.local/BeyondTrust/api/public/v3"

AUTH_KEY = "043f1686e106b3f64c0fcb07b1a66168f09675aa74d7f6999c6109e2628ffe734cc0e26a7c476d6ee217713ff168beabb9f8438bd31637a75f96fd7bd0350ce1"
RUNAS_USER = "btadmin"
EXCEL_FILE_PATH = "excel/data.xlsx"
WORKGROUP_ID = 2  # Beyondtrust Workgroup
DOMAIN_MANAGED_SYSTEM_ID = 2  # Domain'e ait managed system ID
DOMAIN_NAME = "quasys.local"
DEFAULT_AD_PASSWORD = "Qqweqwe"
SMART_RULE_PREFIX = "THY_MA"
LOCAL_GROUP_PERMISSION="[{ PermissionID: 52, AccessLevelID: 1 },	{ PermissionID: 76, AccessLevelID: 3 },	{ PermissionID: 77, AccessLevelID: 1 }]"

TEST_TAG = "btps-auto"

# Windows Managed System create template
WINDOWS_MANAGED_SYSTEM_TEMPLATE = {
    "PlatformID": "1",
    "EntityTypeID": 1,
    "AssetID": None,
    "DatabaseID": None,
    "DirectoryID": None,
    "CloudID": None,
    "FunctionalAccountID": 1,
    "HostName": "",      # Buraya IP adresi gelecek
    "DnsName": "",       # Buraya DNS adı gelecek
    "IPAddress": "",     # Buraya IP adresi gelecek
    "Port": "3389",
    "Timeout": "30",
    "SshKeyEnforcementMode": "0",
    "PasswordRuleID": "0",
    "ReleaseDuration": "120",
    "MaxReleaseDuration": "10079",
    "ISAReleaseDuration": "120",
    "AutoManagementFlag": "true",
    "CheckPasswordFlag": "false",
    "ChangePasswordAfterAnyReleaseFlag": "false",
    "ResetPasswordOnMismatchFlag": "false",
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": "30",
    "ChangeTime": "23:30",
    "RemoteClientType": "None",
    "IsApplicationHost": "false"
}

# Linux Managed System create template

LINUX_MANAGED_SYSTEM_TEMPLATE = {
    "EntityTypeID": 1,
    "WorkgroupID": 2,
    "HostName": "",
    "DnsName": "",
    "IPAddress": "",
    "SystemName": "",
    "PlatformID": 2,
    "Port": 22,
    "Timeout": 30,
    "ReleaseDuration": 120,
    "MaxReleaseDuration": 10079,
    "ISAReleaseDuration": 120,
    "AutoManagementFlag": "false",
    "FunctionalAccountID": "null",
    "LoginAccountID": "null",
    "ElevationCommand": "null",
    "SshKeyEnforcementMode": 0,
    "CheckPasswordFlag": "false",
    "ChangePasswordAfterAnyReleaseFlag": "false",
    "ResetPasswordOnMismatchFlag": "false",
    "ChangeFrequencyType": "first",
    "ChangeFrequencyDays": 30,
    "ChangeTime": "23:30",
    "AccountNameFormat": 0,
    }