import os
import re
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

# Define your time range
start_time = datetime(2024, 7, 1, 0, 0, 0, tzinfo=timezone.utc)  # Example: Start time (UTC)
print(start_time)
end_time = datetime.now(timezone.utc)  # End time is the current time (UTC)
print(end_time)

# client = TelegramClient('session_name', api_id, api_hash)

# def extract_token(url):
#     """Extract token from URL based on common URL patterns."""
#     token_pattern = re.compile(r'/([A-Za-z0-9]{32,})')  # Modify pattern based on your URL structure
#     match = token_pattern.search(url)
#     return match.group(1) if match else 'No token found'

# async def main():
#     # Connect to the client
#     await client.start(phone_number)

#     # Get the channel by its ID
#     channel = PeerChannel(int(channel_id))

#     # Fetch messages from the channel within the specified time range
#     async for message in client.iter_messages(channel, reverse=True):
#         if message.date < start_time:
#             break
#         if start_time <= message.date <= end_time:
#             message_id = message.id
#             message_text = message.message
#             received_at = message.date.strftime('%Y-%m-%d %H:%M:%S')

#             # Extract and print hyperlinks
#             links = []
#             tokens = []
#             if message.entities:
#                 for entity in message.entities:
#                     if isinstance(entity, MessageEntityTextUrl):
#                         url = entity.url
#                         links.append(url)
#                         token = extract_token(url)
#                         tokens.append(token)

#             links_str = ', '.join(links) if links else 'No links'
#             tokens_str = ', '.join(tokens) if tokens else 'No tokens'

#             # Print the message, hyperlinks, and tokens
#             print(f"Message ID: {message_id}")
#             print(f"Message Text: {message_text}")
#             print(f"Received At: {received_at} UTC")
#             print(f"Links: {links_str}")
#             print(f"Tokens: {tokens_str}")
#             print('-' * 40)

#         elif message.date < start_time:
#             break

# # Run the client
# with client:
#     client.loop.run_until_complete(main())
