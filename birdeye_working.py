import requests
from datetime import datetime, timezone, timedelta

def get_prices(token, time_from, time_to):
    url = f"https://public-api.birdeye.so/defi/history_price?address={token}&address_type=pair&type=1m&time_from={time_from}&time_to={time_to}"

    headers = {
        "x-chain": "solana",
        "X-API-KEY": "ad9f3160a81043079d0e34a3acfd8cd5"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        items = data['data']['items']
        highest_price_item = max(items, key=lambda x: x['value'])
        starting_price_item = items[0] if items else None

        highest_price = highest_price_item['value']
        highest_timestamp = highest_price_item['unixTime']
        starting_price = starting_price_item['value'] if starting_price_item else None
        starting_timestamp = starting_price_item['unixTime'] if starting_price_item else None

        # Calculate time difference
        if starting_timestamp and highest_timestamp:
            time_to_highest = highest_timestamp - starting_timestamp
            time_to_highest_human_readable = str(timedelta(seconds=time_to_highest))
        else:
            time_to_highest_human_readable = "N/A"

        # Calculate percentage change
        if starting_price and highest_price:
            percentage_change = ((highest_price - starting_price) / starting_price) * 100
        else:
            percentage_change = None

        # Convert Unix timestamp to human-readable format
        highest_timestamp_human_readable = datetime.fromtimestamp(highest_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') if highest_timestamp else "N/A"
        starting_timestamp_human_readable = datetime.fromtimestamp(starting_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') if starting_timestamp else "N/A"

        return {
            "highest_price": highest_price,
            "highest_price_time": highest_timestamp_human_readable,
            "starting_price": starting_price,
            "starting_price_time": starting_timestamp_human_readable,
            "time_to_highest": time_to_highest_human_readable,
            "percentage_change": percentage_change
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {e}"}
    except KeyError as e:
        return {"error": f"Data parsing error: Missing key {e}"}

def convert_to_unix_time(datetime_str):
    # Parse the datetime string to a datetime object with timezone awareness
    dt = datetime.fromisoformat(datetime_str)
    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

# Example usage
datetime_str_from = "2024-07-25 06:30:11+00:00"
unix_timestamp_from = convert_to_unix_time(datetime_str_from)
print(f"The Unix timestamp from is: {unix_timestamp_from}")

datetime_str_to = "2024-07-25 16:00:00+00:00"
unix_timestamp_to = convert_to_unix_time(datetime_str_to)
print(f"The Unix timestamp to is: {unix_timestamp_to}")

# Example usage
token = "63eKybB1QAoTEqLX6nnroJx97C9ZK2gbWbKjMfx1NwFL"

prices_info = get_prices(token, unix_timestamp_from, unix_timestamp_to)
print(f"The highest price is: {prices_info.get('highest_price')}")
print(f"The highest price was reached at: {prices_info.get('highest_price_time')}")
print(f"The starting price is: {prices_info.get('starting_price')}")
print(f"The starting price was at: {prices_info.get('starting_price_time')}")
print(f"Time to reach highest price: {prices_info.get('time_to_highest')}")
print(f"Percentage change from starting price to highest price: {prices_info.get('percentage_change'):.2f}%")
