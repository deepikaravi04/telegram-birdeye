from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
import asyncio
import requests
from datetime import datetime, timezone, timedelta
import re
import pandas as pd

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
            "starting_price_time": starting_timestamp_human_readable,
            "starting_price": starting_price,
            "highest_price_time": highest_timestamp_human_readable,
            "highest_price": highest_price,
            "time_to_highest": time_to_highest_human_readable,
            "percentage_change": percentage_change
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {e}"}
    except KeyError as e:
        return {"error": f"Data parsing error: Missing key {e}"}

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

async def read_channel_messages_by_id(channel_id, limit=25):
    start_time, end_time = get_time_range()
    time_to = convert_to_unix_time(end_time)
    results = []

    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        count = 0
        async for message in client.iter_messages(channel_id, limit=limit):
            message_date = message.date
            if start_time <= message_date <= end_time:
                time_from = convert_to_unix_time(message_date)
                token = get_token_from_message_url(message)
                if token:
                    price_info = get_prices(token, time_from, time_to)
                    if 'error' not in price_info:
                        count += 1
                        print(count)
                        price_info.update({"token": "https://birdeye.so/token/So11111111111111111111111111111111111111112/"+ token +"?chain=solana"})
                        results.append(price_info)
                    await asyncio.sleep(5)  # avoid hitting rate limits

    return results

def format_results(results):
    df = pd.DataFrame(results)
    df_sorted = df.sort_values(by="percentage_change", ascending=False)
    
    # Save to CSV
    csv_file = 'token_statistics.csv'
    df_sorted.to_csv(csv_file, index=False)
    
    output = "**23 July best signals & statistics:**\n\n"

    for i, row in df_sorted.iterrows():
        output += f"**#{i+1} {row['token']} - {row['percentage_change']:.2f}%**\n"
        output += f"You could've got {row['percentage_change']:.2f}%\nwithin {row['time_to_highest']} from signal.\n\n"

    output += "**Total winners:**\n"
    output += f"Increased 2x: {sum(df['percentage_change'] > 100)}\n"
    output += f"Increased 3x: {sum(df['percentage_change'] > 200)}\n"
    output += f"Increased 5x: {sum(df['percentage_change'] > 400)}\n"

    # Example signals, replace with actual logic if needed
    output += "SignalA: 25\nSignalB: 11\nSignalD: 5\n"

    return output, csv_file

if __name__ == "__main__":
    results = asyncio.run(read_channel_messages_by_id(channel_id))
    report, csv_file = format_results(results)
    print(report)
    print(f"CSV file saved at: {csv_file}")
