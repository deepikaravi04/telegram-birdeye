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
            "time_to_highest": timedelta(seconds=time_to_highest), 
            "percentage_change": percentage_change
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request error: {e}"}
    except KeyError as e:
        return {"error": f"Data parsing error: Missing key {e}"}

def get_time_range():
    now = datetime.now(timezone.utc)
    end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=2)
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

async def read_channel_messages_by_id(channel_id, limit=50, reverse=True):
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
                token_name = extract_token_name(message.message)
                
                if token:
                    price_info = get_prices(token, time_from, time_to)
                    if 'error' not in price_info:
                        count += 1
                        print(count)
                        price_info.update({"token": "https://birdeye.so/token/So11111111111111111111111111111111111111112/"+ token +"?chain=solana"})
                        price_info.update({"token_name": token_name})
                        results.append(price_info)

                    await asyncio.sleep(2)  # avoid hitting rate limits

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
    df_sorted = df.sort_values(by="percentage_change", ascending=False)
    df_top = df.sort_values(by="percentage_change", ascending=False).head(10)
    # Save to CSV
    csv_file = 'token_statistics.csv'
    df_sorted.to_csv(csv_file, index=False)
    
    # Count total signals, positive, and zero/negative percentage changes
    total_signals = len(df_sorted)
    total_positive_percentage = sum(df_sorted['percentage_change'] > 0)
    total_zero_or_negative_percentage = total_signals - total_positive_percentage
    
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    yesterday_date = yesterday.strftime("%d %B")
    output = "<b>"+ yesterday_date+" best signals & statistics:</b>\n\n"
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
            output += f"You could've got {row['percentage_change']:.2f}%\n"
            output += f"within {time_to_highest_readable} from signal.\n\n"
            count += 1

    output += "<b>Total Winners:</b>\n"
    output += f"Increased 2x (100%+): {sum(df_sorted['percentage_change'] > 100)}\n"
    output += f"Increased 3x (200%+): {sum(df_sorted['percentage_change'] > 200)}\n"
    output += f"Increased 5x (400%+): {sum(df_sorted['percentage_change'] > 400)}\n"
    
    # Add total signals and percentage counts to the output
    output += f"\n<b>Total Signals:</b> {total_signals}\n"
    output += f"<b>Total Positive Percentage Changes:</b> {total_positive_percentage}\n"
    output += f"<b>Total Zero or Negative Percentage Changes:</b> {total_zero_or_negative_percentage}\n"

    return output

if __name__ == "__main__":
    results = asyncio.run(read_channel_messages_by_id(channel_id))
    report = format_results(results)
    
    # Replace with your Telegram channel ID
    channel_id = "-1002218204095"
    
    # Replace with your bot token obtained from BotFather
    bot_token = "7286220618:AAHVIE9mpwiVcwZBLut3WpXpeFBUnoe9IeU"
    
    send_report_to_channel(channel_id, report)