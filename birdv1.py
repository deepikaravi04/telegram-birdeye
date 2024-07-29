from telethon import TelegramClient
import asyncio

# Replace these with your actual API ID, API Hash, and phone number
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = -1002235691978  # Replace with your channel ID

async def read_channel_messages_by_id(channel_id, limit=250):
    # Create the client and connect
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Ensure the client is connected
        await client.start(phone=phone_number)
        count = 0
        # Fetch messages from the channel using the channel ID
        async for message in client.iter_messages(channel_id, limit=limit):
            print(f"Date: {message.date}")
            count += 1
        print(count)
    
# Example usage
if __name__ == "__main__":
    asyncio.run(read_channel_messages_by_id(channel_id))
    