from telethon import TelegramClient, sync
from datetime import datetime
import asyncio

# Replace these with your actual API ID, API Hash, and phone number
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = -1002235691978  # Replace with your channel ID


async def fetch_messages(channel_id, limit=2000):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        await client.start(phone=phone_number)
        
        # Fetch the last 'limit' messages
        messages = []
        async for message in client.iter_messages(channel_id, limit=limit):
            messages.append(message)
        
        return messages

if __name__ == "__main__":
    messages = asyncio.run(fetch_messages(channel_id))
    count = 0
    for message in messages:
        print(f"Date: {message.date} | Sender: {message.sender_id} | Message: {message.text}")
        count += 1
    print(count, "$"* 40)