import os
import re
import asyncio
from datetime import datetime, timezone
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, MessageEntityTextUrl
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Replace these with your actual values
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
channel_id = '-1002235691978'

client = TelegramClient('session_name', api_id, api_hash)

def extract_token(url):
    """Extract token from URL based on common URL patterns."""
    token_pattern = re.compile(r'/([A-Za-z0-9]{32,})')  # Modify pattern based on your URL structure
    match = token_pattern.search(url)
    return match.group(1) if match else 'No token found'

async def fetch_and_print_messages():
    print("Connecting to the client...")
    await client.start(phone_number)
    print("Client connected.")

    # Get the channel by its ID
    channel = PeerChannel(int(channel_id))
    print(f"Fetching messages from channel: {channel_id}")

    # Fetch messages from the channel
    async for message in client.iter_messages(channel, limit=250):
        if message:
            # Print message date and its timezone info
            message_date = message.date
            print(f"Message date: {message_date} (Timezone: {message_date.tzinfo})")
            print("#" * 40)

            message_id = message.id
            message_text = message.message
            received_at = message_date.strftime('%Y-%m-%d %H:%M:%S')

            # Extract and print hyperlinks
            links = []
            tokens = []
            if message.entities:
                for entity in message.entities:
                    if isinstance(entity, MessageEntityTextUrl):
                        url = entity.url
                        links.append(url)
                        token = extract_token(url)
                        tokens.append(token)

            links_str = ', '.join(links) if links else 'No links'
            tokens_str = ', '.join(tokens) if tokens else 'No tokens'

            # Print the message, hyperlinks, and tokens
            print(f"Message ID: {message_id}")
            print(f"Message Text: {message_text}")
            print(f"Received At: {received_at} UTC")
            print(f"Links: {links_str}")
            print(f"Tokens: {tokens_str}")
            print('-' * 40)
        else:
            print("No messages found.")
        

# Run the client and execute the function
with client:
    client.loop.run_until_complete(fetch_and_print_messages())