from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
import asyncio
import requests
from datetime import datetime, timezone, timedelta
import re

# Replace these with your actual API ID, API Hash, and phone number
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = -1002235691978  # Replace with your channel ID

def convert_to_unix_time(dt):
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

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
        if not items:
            return {"error": "No data available for the given time range."}

        highest_price_item = max(items, key=lambda x: x['value'])
        starting_price_item = items[0]

        highest_price = highest_price_item['value']
        highest_timestamp = highest_price_item['unixTime']
        starting_price = starting_price_item['value']
        starting_timestamp = starting_price_item['unixTime']

        time_to_highest = highest_timestamp - starting_timestamp
        time_to_highest_human_readable = str(timedelta(seconds=time_to_highest))

        percentage_change = ((highest_price - starting_price) / starting_price) * 100

        highest_timestamp_human_readable = datetime.fromtimestamp(highest_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        starting_timestamp_human_readable = datetime.fromtimestamp(starting_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

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
    except ValueError as e:
        return {"error": f"Value error: {e}"}

def get_time_range():
    now = datetime.now(timezone.utc)
    end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)
    return start_time, end_time

def extract_token(url):
    token_pattern = re.compile(r'/([A-Za-z0-9]{32,})')  # Modify pattern based on your URL structure
    match = token_pattern.search(url)
    return match.group(1) if match else 'No token found'

def get_token_from_message_url(message):
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, MessageEntityTextUrl):
                url = entity.url
                return extract_token(url)
    return None

async def read_channel_messages_by_id(channel_id, limit=250):
    start_time, end_time = get_time_range()
    time_from, time_to = convert_to_unix_time(start_time), convert_to_unix_time(end_time)
    results = []

    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        count = 0
        async for message in client.iter_messages(channel_id, limit=limit):
            message_date = message.date
            if start_time <= message.date <= end_time:
                token = get_token_from_message_url(message)
                if token:
                    price_info = get_prices(token, time_from, time_to)
                    count += 1
                    print(count)
                    if 'error' not in price_info:
                        results.append({
                            "token": token,
                            "percentage_change": price_info["percentage_change"],
                            "time_to_highest": price_info["time_to_highest"]
                        })
                    await asyncio.sleep(5)  # avoid hitting rate limits

    return results

def format_results(results):
    sorted_results = sorted(results, key=lambda x: x["percentage_change"], reverse=True)[:10]
    output = "**23 July best signals & statistics:**\n\n"

    for i, result in enumerate(sorted_results, start=1):
        output += f"**#{i} {result['token']} - {result['percentage_change']:.2f}%**\n"
        output += f"You could've got {result['percentage_change']:.2f}%\nwithin {result['time_to_highest']} from signal.\n\n"

    output += "**Total winners:**\n"
    output += f"Increased 2x: {sum(1 for r in results if r['percentage_change'] > 100)}\n"
    output += f"Increased 3x: {sum(1 for r in results if r['percentage_change'] > 200)}\n"
    output += f"Increased 5x: {sum(1 for r in results if r['percentage_change'] > 400)}\n"

    # Example signals, replace with actual logic if needed
    output += "SignalA: 25\nSignalB: 11\nSignalD: 5\n"

    return output

if __name__ == "__main__":
    results = asyncio.run(read_channel_messages_by_id(channel_id))
    report = format_results(results)
    print(report)
