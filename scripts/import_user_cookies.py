import json
from pathlib import Path

raw_cookies_str = """
[
    {
        "domain": ".pinterest.com",
        "expirationDate": 1818797326.88641,
        "hostOnly": false,
        "httpOnly": false,
        "name": "_b",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "\\"AZa+9HIwItBL/JoUrFJHK/B/IQR6kQcgj8y8CaYzyobz+71PvPN0SOSDPkY4kocF5M4=\\""
    },
    {
        "domain": ".pinterest.com",
        "expirationDate": 1815341330.585326,
        "hostOnly": false,
        "httpOnly": true,
        "name": "_pinterest_sess",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "TWc9PSYxTXNzRGFwcTh4dG45TWZ1K1pvWGZpUVc0c1BBSmJ6Z3hZZ005UWtwWDJ0WDF4Tkx0NmU0RkhrT0k0RTU2cG5qZDJZQVpTMDBGUUFoNXlDZkNzWEtYRnJrcEJoZ0pKMHR0YitRVjhnWnBKTmZkWWM5ZUhpT0tyUUl0cVdGYUwwL1d3Mk5sV1lYbTQrK3lWbGVRaVFXN3FXcksrUkY2dUc4YURWb1BaZzFSeWNVNStYQVJESXBDMHN6bjd1OCtGVFNBNTM2blNQTWhrWmJ0RXBIaWMxZEQyaDYzYkRZa3d6N09oM1lpRmw5UTBRWnRtTWVhQW5SMXVjMlpiV01qdHFZT1RaREpQdWxOVjNmeVk1K05vekljWHFPeXhSeVNuai9ud256bS81aktQUndabzhHNEJwRFhUVHhCME8zWUZtOGVxUDZZMXRRSUhQRlFxMUVCZnNQVGFrTkVFQVA3ZHE4VjgvUEk3dmxNY25CSm0vemV4anZFcnpBYzBzbVFxWHAxRHRxY3VuZ2o5MXhYa2xsY000V0ZIemFiSFk1bDU5bjc1ZWZIRDJJQnh1TU1aUlJJU3YwSGkrMEJiUlVQb0ZYM2ZBZGpFWEJlc3RlM28wR3FmOXJ1OGZFLzArbG1qSlR5cHY0TmR6SFdZNmNTYkw4S3I3TXY0Wll6ZXlDRmZjYys1SjJNbjUwSGtMbDR0NWF3Q25hWUlBMWFIZE9kTDlidStLZTcxTitRRFEzT1Z1bmkycjhKL2R1eVc2U205U1NaYnlERVc4UDZxLy9CRGQzRXU2UEZFcmZCLzlMOU0xQm5GeTlXM3NFMDBsR01aKzhBTCs1SUZvZXBzZUpBTWpPbnlIcnFzTEpCRkoyNEJtRjYyVUlnNWFvQVVzUmN5U3NQN3d4R0FFS25Oa0phYVVJT0x6Q1M5cGRGUHo2SVpWSTNubmp0SzliaTRRRzhPKzZLRFlrN0hUdm9VQm5wVEo1T0dSMzJpWk8vK3lheHFDb0hic1huam96cVpUSXk3K3MrMWYxSE9DY3Y1M3BCWUt1TFY3SEkyRlZmQlErd0tIeHg0YU4wU2FnNjZncjRrY3hBc2gydHJhWGZmTW1ETEtFelBoN1NhWG9JN3h2YnRodnNubXlxbDdXVS9uMFppV1RMMU5UeGxhdlhKU0l1dlo3bVJSaVF6RzQxWkh6Z3RYeC84TExkVWhCaXJIQ1B1QVdrdkZlZ0xyUDluVlgyOFdNR0tQVFJZeGlOZEIyUEg4d0VSWEcrTWs1bWRDRTVQZ2N4QlkwN0NzNlg5cnRhMUNQUU9JcVhTR3pCaFZNaGRPRUx2TFNhR0Y1QTFjRjZYbDJRdGxuSUVZcFRBRHVnSDhYbVV6VlpnS1hMZXV6KzIxQXE0cXNjY1JBOTYzSlVLZnN1TGxENW5rN1Z2cGFZSVFkenNuWUIxVEtyRjRpQVI0cWRQUWNmT2JUV0NXSFdpWEF6WXdpeTgrblNjMDJqMk1LK1BBVWN1TTFYM2cvZ2JKWk5XNWMzTXRuKzBmcVljSUdBKytVUXd2SEo3WlMrV2pYRVpFdktJMTA5NTIrVURwSFUyTnVzNTVUNmJ3YWtNOGtVdFJFU2ttcWhTLzg5UmlhYmp3UGt4TldqNGhKblBndWsrNUZ2Z0ZINXlwZUVhQXBFZnUybXZUWjRoakM2cjhBL2gzOFRoUHltZmVhcmJUOWpwWEpDLzI3Z05qVXN1UVgraDJhSWNqa2NZWmZwSUEzREl0dTdnalIwOXlweGxnNExiYjVXL1hVOUNEUUhCNlgmWVZlSXU5eDQrQzlmaE5SdDVmdUxHc2I5NDlrPQ=="
    },
    {
        "domain": ".pinterest.com",
        "expirationDate": 1815341330.585512,
        "hostOnly": false,
        "httpOnly": true,
        "name": "__Secure-s_a",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "Vk43ZW9MenJQLzVUaEdLbFZCSlV0Y0RTOG4wVHh1c3V2cWhDNlcyZHlYTDJONC90b3VtbHpScENvRlJFS05vL3BiM0FzMGgvbXY2UUN3NjdRM0RLYkdVZURJdENiRngwNW84V1NaTEkreHlBVHdCYkxqYWxlTHE1Z0pyRGhiSFRYWGVSNHNXSjlUcXNFNFlWNmtLdHZRcUJQMmdMMWM4MUgwQU5qOHNJSk1IVmNkUGR0aVdnN0FMUHZZQWU3SEdCUlZTQ1ArWC9PSEdaZnRSMzkvRHJVZFZaRm9sd2hoTDA0Rkw5alJwdkZWeWtNempQSHRyYUMrY3hsZ09jZXVhejY5ZWt3SEhsOHI0OFZRVjhUZFhoZGw4aTN0Z1JtS2g1STJLdUZMeU1mdUhEL2xtODNPa0dKNk5ybTJzbnNmOG9vL1ZkVXFJUVlSbzdrV214d0dzRDRqUERBdVJ3d1AyWCs2Z0xsTGtndEo0YUMwRTV4UW1wZ05lRlphUVNmSlI0UEJnL2EyaXB3QVNqc1Y1THk3cFI5VUhlWG1CNy9KMGtBYlZzaUoxNVRYSWt0R2loWk9WV3NrbklNRWpyK2p6dzZzT25UWmt4WnJ4bmpVeFJrRzhLb05ldnZ4cUkzWU5GOHJ5WG1RME9mR1JFeUk5QTVjSTNlWUsreElDRUhVM2JnNExMOGdyYTR5ejVIM3FwQmszaEpQUUNLcUdhamVkN3JHWTRNTzQ0NFh0T0I4Q2o4UCtSOXZxdU5LdU1WM1BoeFdrbE9yWi8xN0xiOS9YWWJQUEV2aFBrZFYxbDEyOWo0dkkwaTJ4ZG9lVFg2bUUvTWpVRkF1czhCVDJSNzZZdDFVMVlqeVFOdzJnT1I2dmpvbzRRUXQ5NDdQelVlVWhFbHRPcm5LNE9HQ1ZJREFnb3JuU2ozUjBXSkNaMG9QN1VuRnJJMEhoaDh4RS9acyt1VHBlUnYySTQ3N3Z3Ymc5MzZqV3RHSGE0UE5PUkMvTysyY2owamVYeTdyZjE2ZGx0VXdaNlRjMmxrV1ZNeHo1QmVNQVFuNU9veG1pSFZJZ1psSEQvUk5SNmdpTjJkenVsQ0Z6UHZrTXEyMnRpazJPeWdCRURPMklubm54WVRRaDJmb3BZbTF5NW51RlRlQ3laMUZGbkp4SFRsb3d5Umd3S1V2K0M0eURXcXNPa0FGNkNsEIkxeDhzazk5UFR5cngreWJTOTVwT0R6VUJDdERMUUpURWg5WGVrcjVjRHd6blZEU1dVV05NZ1Nnank1WUFja0ViMFBteUc1aVRHWUkwQlJWYytkVHFNcEMxZnhkMEhaZ1NsellLMG5HST0mNXRYcHBCWnBaRzVLMDZtdWpmRW00MjhqeHFjPQ=="
    },
    {
        "domain": ".pinterest.com",
        "expirationDate": 1815341330.585156,
        "hostOnly": false,
        "httpOnly": true,
        "name": "_auth",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1"
    },
    {
        "domain": "br.pinterest.com",
        "expirationDate": 1784323724.60962,
        "hostOnly": true,
        "httpOnly": true,
        "name": "_routing_id",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "\\"979b73aa-e7e2-4dc6-91eb-9ae2b8ca26e3\\""
    },
    {
        "domain": "br.pinterest.com",
        "expirationDate": 1815773324.609475,
        "hostOnly": true,
        "httpOnly": false,
        "name": "csrftoken",
        "path": "/",
        "sameSite": "lax",
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "159b7239afcd3b629d1d1a325736f7fd"
    },
    {
        "domain": "br.pinterest.com",
        "expirationDate": 1799813334,
        "hostOnly": true,
        "httpOnly": false,
        "name": "g_state",
        "path": "/",
        "sameSite": null,
        "secure": false,
        "session": false,
        "storeId": null,
        "value": "{\\"i_l\\":0,\\"i_ll\\":1784261334004,\\"i_e\\":{\\"enable_itp_optimization\\":24},\\"i_et\\":1784261334004,\\"i_b\\":\\"1cHcBfoEIM2xEJLEtKw3QWUbasebYJlwZhMNIA8n52U\\"}"
    },
    {
        "domain": ".pinterest.com",
        "expirationDate": 1818797330.585463,
        "hostOnly": false,
        "httpOnly": true,
        "name": "l_o",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "bx9V21ylCOKRM8C5e4+OUJE63pQjgDyqTpUhDdJs1bYNP5VWLr8Jkye7CZgPhjlhmIKD2CWCDC6fALVkq76kN4367TrCnu21hqnhoE1ZoX3UY2EXmKxZ3YPSXU93C72HPEU="
    },
    {
        "domain": "br.pinterest.com",
        "expirationDate": 1784280525,
        "hostOnly": true,
        "httpOnly": false,
        "name": "sessionFunnelEventLogged",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "1"
    }
]
"""

raw_cookies = json.loads(raw_cookies_str)

playwright_cookies = []
for cookie in raw_cookies:
    pw_cookie = {
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie["path"],
        "expires": cookie.get("expirationDate"),
        "httpOnly": cookie.get("httpOnly", False),
        "secure": cookie.get("secure", False),
    }
    ss = cookie.get("sameSite")
    if ss == "no_restriction":
        pw_cookie["sameSite"] = "None"
    elif ss == "lax":
        pw_cookie["sameSite"] = "Lax"
    elif ss == "strict":
        pw_cookie["sameSite"] = "Strict"
    else:
        pw_cookie["sameSite"] = "Lax"
        
    playwright_cookies.append(pw_cookie)

sessions_dir = Path("config/sessions")
sessions_dir.mkdir(parents=True, exist_ok=True)
dest_path = sessions_dir / "pinterest.json"

state_data = {
    "cookies": playwright_cookies,
    "origins": []
}

with open(dest_path, "w", encoding="utf-8") as f:
    json.dump(state_data, f, indent=2)

print(f"Cookies importados e salvos com sucesso em: {dest_path}")
