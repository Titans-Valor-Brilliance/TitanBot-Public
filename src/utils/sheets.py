from src.utils.titan import titan
import requests
import time
import jwt

def new_capt_apps():
    url = "https://oauth2.googleapis.com/token"
    pay = {
        "iss": "change",
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "aud": "https://oauth2.googleapis.com/token",
        "exp": int(time.time())+3600,
        "iat": int(time.time())
    }
    a = jwt.encode(pay, titan.cred["private_key"], algorithm='RS256')
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": str(a)[2:-1]
    }
    r = requests.post(data=payload, url=url).json()
    access = r["access_token"]
    a = requests.get(url="https://sheets.googleapis.com/v4/spreadsheets/1xptBPOJ0F8M3geEtgX2ZYW7EG9MrR1OzJnwUiZV8Xzg/values/A1:Z1000", headers={"Authorization": "Bearer "+access}).json()
    print(a)
    return a