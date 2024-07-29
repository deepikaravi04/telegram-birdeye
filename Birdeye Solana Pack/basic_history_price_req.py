import requests

url = "https://public-api.birdeye.so/defi/history_price?address=8MFuYqWR27utRZ14Pkt88TaxBWXR7Xb31k7UyMdxMjcM&address_type=pair&type=1m&time_from=1721837702&time_to=1721837942"

headers = {
    "x-chain": "solana",
    "X-API-KEY": "ad9f3160a81043079d0e34a3acfd8cd5"
}

response = requests.get(url, headers=headers)

print(response.text)