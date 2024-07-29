import requests
import json
from datetime import datetime, timezone
url = "https://public-api.birdeye.so/defi/history_price?address=8MFuYqWR27utRZ14Pkt88TaxBWXR7Xb31k7UyMdxMjcM&address_type=pair&type=1m&time_from=1721837702&time_to=1721868992"

headers = {
    "x-chain": "solana",
    "X-API-KEY": "ad9f3160a81043079d0e34a3acfd8cd5"
}

response = requests.get(url, headers=headers)

# print(response.text)
response_data = json.loads(response.text)

items = response_data['data']['items']

# Print each item's details
for item in items:
    address = item['address']
    unix_time = item['unixTime']
    value = item['value']
    
    # Convert unix time to a readable format with timezone-aware UTC
    readable_time = datetime.fromtimestamp(unix_time, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Address: {address}, Time: {readable_time}, Value: {value}")