import requests
import json

def get_access_token():
    url = 'https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    payload = {'app_id': 'cli_a4975aa52a78d00a', 'app_secret': '0rLOYN8BL1x6VkU0RgEepbvcDO6ZBVyo'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

