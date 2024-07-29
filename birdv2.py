from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
import asyncio
from datetime import datetime, timedelta, timezone
import re

# Replace these with your actual API ID, API Hash, and phone number
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = -1002235691978  # Replace with your channel ID


def get_time_range():
    """Calculate the start and end time for the time range."""
    now = datetime.now(timezone.utc)
    end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=1)
    return start_time, end_time


def extract_token(url):
    """Extract token from URL based on common URL patterns."""
    token_pattern = re.compile(r'/([A-Za-z0-9]{32,})')  # Modify pattern based on your URL structure
    match = token_pattern.search(url)
    return match.group(1) if match else 'No token found'

def get_token_from_message_url(message):
    links = []
    tokens = []
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, MessageEntityTextUrl):
                url = entity.url
                links.append(url)
                token = extract_token(url)
                tokens.append(token)
    return tokens[0]

async def read_channel_messages_by_id(channel_id, limit=250):
    # Create the client and connect
    start_time, end_time = get_time_range()
    print(start_time, end_time)

    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Ensure the client is connected
        await client.start(phone=phone_number)

        # Fetch messages from the channel using the channel ID
        async for message in client.iter_messages(channel_id, limit=limit):
            message_date = message.date
            if start_time <= message.date <= end_time:
                print(f"Message date: {message_date} (Timezone: {message_date.tzinfo})")
                token = get_token_from_message_url(message)
                print(token)

    
# Example usage
if __name__ == "__main__":
    asyncio.run(read_channel_messages_by_id(channel_id))

