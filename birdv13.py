from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
import asyncio
import requests
from datetime import datetime, timezone, timedelta
import re
import pandas as pd
import numpy as np
import time
import logging

# Replace these with your actual API ID, API Hash, and phone number
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = -1002235691978  # Replace with your channel ID

def convert_to_unix_time(dt):
    return int(dt.timestamp())

def get_prices(token, time_from, time_to, retries=5):
    url = f"https://public-api.birdeye.so/defi/history_price?address={token}&address_type=pair&type=1m&time_from={time_from}&time_to={time_to}"

    headers = {
        "x-chain": "solana",
        "X-API-KEY": "ad9f3160a81043079d0e34a3acfd8cd5"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data['data']['items']
            if not items:
                return {"error": "No data items returned"}

            highest_price_item = max(items, key=lambda x: x['value'])
            starting_price_item = items[0]

            highest_price = highest_price_item['value']
            highest_timestamp = highest_price_item['unixTime']
            starting_price = starting_price_item['value']
            starting_timestamp = starting_price_item['unixTime']

            # Calculate time difference
            time_to_highest = highest_timestamp - starting_timestamp
            time_to_highest_human_readable = str(timedelta(seconds=time_to_highest))

            # Calculate percentage change
            percentage_change = ((highest_price - starting_price) / starting_price) * 100

            # Convert Unix timestamp to human-readable format
            highest_timestamp_human_readable = datetime.fromtimestamp(highest_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
            starting_timestamp_human_readable = datetime.fromtimestamp(starting_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

            return {
                "starting_price_time": starting_timestamp_human_readable,
                "starting_price": starting_price,
                "highest_price_time": highest_timestamp_human_readable,
                "highest_price": highest_price,
                "time_to_highest": timedelta(seconds=time_to_highest),
                "percentage_change": percentage_change
            }

        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)  # Wait 1 second before retrying

    return {"error": "API request failed after multiple attempts"}

def get_time_range():
    now = datetime.now(timezone.utc)
    end_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
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

def extract_token_name(message_text):
    # Assuming the token name is the first part of the message before the first URL
    # Split the message by '|' and take the first part
    parts = message_text.split('|')
    if parts:
        token_name_part = parts[0].strip()  # Get the first part and strip whitespace
        return token_name_part
    return None

def extract_a_substring_signal_name(text):
    # Find the index of the last pipe character
    pipe_index = text.rfind('|')
    
    # If no pipe character is found, return None
    if (pipe_index == -1) or (pipe_index == len(text) - 1):
        return None
    
    # Extract the substring starting from the pipe index
    substring = text[pipe_index+1:]
    
    # Check if the substring matches 'a1' or 'a10'
    return substring.strip()

async def fetch_messages(channel_id, limit=1000):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        
        # Fetch the last 'limit' messages
        messages = []
        async for message in client.iter_messages(channel_id, limit=limit):
            messages.append(message)
        
        return messages

async def read_channel_messages_from_telegram(channel_id, start_time, end_time):
    time_to = convert_to_unix_time(end_time)
    results = []
    token_list = []
    print(start_time, end_time)
    messages = await fetch_messages(channel_id)
    for message in messages:
        message_date = message.date
        token_name = extract_token_name(message.message)
        print(message_date)
        print(token_name)
        if start_time <= message_date <= end_time and '⛔️' not in token_name and token_name not in token_list:
            time_from = convert_to_unix_time(message_date)
            token = get_token_from_message_url(message)
            token_name = extract_token_name(message.message)
            signal_name = extract_a_substring_signal_name(message.message)
            token_list.append(token_name)
            print(token_name, signal_name)
            if token:
                price_info = get_prices(token, time_from, time_to)
                if 'error' not in price_info:
                    print(f"Processed token: {token_name}")
                    price_info.update({"token": "https://birdeye.so/token/"+ token +"?chain=solana"})
                    price_info.update({"token_name": token_name})
                    price_info.update({"signal_name": signal_name})
                    results.append(price_info)
                await asyncio.sleep(3)  # avoid hitting rate limits

    return results

def send_report_to_channel(chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    # Split the text into chunks of up to 4096 characters
    for i in range(0, len(text), 4096):
        chunk = text[i:i + 4096]
        data = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an error for bad responses

def format_results(results):
    df = pd.DataFrame(results)
    grouped_df = df.groupby('signal_name')

    # Calculate the number of profitable trades for each signal
    profitable_trades = grouped_df['percentage_change'].apply(lambda x: (sum(x > 50), len(x)))

    # Print the number of profitable trades for each signal
    df_sorted = df.sort_values("percentage_change", ascending=False)
    df_top = df_sorted.head(10)
    csv_file = 'token_statistics.csv'
    df_sorted.to_csv(csv_file, index=False)

    # Count total signals, positive, and zero/negative percentage changes
    total_signals = len(df_sorted)
    total_positive_percentage = sum(df_sorted['percentage_change'] > 0)
    total_zero_or_negative_percentage = total_signals - total_positive_percentage

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_date = yesterday.strftime("%d %B")
    output = f"<b>{yesterday_date} best signals & statistics:</b>\n\n"

    count = 1
    for i, row in df_top.iterrows():
        if row.percentage_change > 1:
            # Convert the time_to_highest to a more readable format
            total_seconds = int(row['time_to_highest'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_parts = []
            if hours == 0:
                time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if hours > 0:
                time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            time_to_highest_readable = ' '.join(time_parts) if time_parts else "0 minutes"
           
            token_link = f"<a href='{row['token']}'>{row['token_name']}</a>"
            output += f"<b>#{count} {token_link} - {row['percentage_change']:.2f}%</b>\n"
            output += f"You could've got {row['percentage_change']:.2f}% profit\n"
            output += f"within {time_to_highest_readable} from our signal.\n\n"
            count += 1

    output += "<b>Total Winners:</b>\n"
    output += f"Increased 10x (900%+): {sum(df_sorted['percentage_change'] > 900)}\n"
    output += f"Increased 5x (400%+): {sum(df_sorted['percentage_change'] > 400)}\n"
    output += f"Increased 3x (200%+): {sum(df_sorted['percentage_change'] > 200)}\n"
    output += f"Increased 2x (100%+): {sum(df_sorted['percentage_change'] > 100)}\n"
    output += f"Increased 1.5x (50%+): {sum(df_sorted['percentage_change'] > 50)}\n"

    # Add total signals and percentage counts to the output
    output += f"\n<b>Total Signals:</b> {total_signals}\n"
    output += f"<b>Total Positive Percentage Changes:</b> {total_positive_percentage}\n"
    output += f"<b>Total Zero or Negative Percentage Changes:</b> {total_zero_or_negative_percentage}\n\n\n"

    output += "<b>Profitable Trades for Each Signal</b>:\n"
    for signal, (profitable, total) in profitable_trades.items():
        profitability_percent = (profitable / total) * 100
        if profitability_percent > 50:
            output += f"<b>{signal}</b>: {profitable}/{total} ({profitability_percent:.2f}% profitable)\n"
        else:
            output += f"<b>{signal}</b>: {profitable}/{total} ({profitability_percent:.2f}%)\n"
    return output

if __name__ == "__main__":  
    start_time, end_time = get_time_range()
    # start_time = datetime(2024, 7, 28, 0, 0, 0, tzinfo=timezone.utc)
    # end_time = datetime(2024, 7, 29, 0, 0, 0, tzinfo=timezone.utc)
    results = asyncio.run(read_channel_messages_from_telegram(channel_id, start_time, end_time))
    print(results)
    report = format_results(results)
    
    # Replace with your Telegram channel ID for sending the report
    report_channel_id = "-1002218204095"
    
    # Replace with your bot token obtained from BotFather
    bot_token = "7286220618:AAHVIE9mpwiVcwZBLut3WpXpeFBUnoe9IeU"
    
    send_report_to_channel(report_channel_id, report)
