from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel

# Replace 'YOUR_API_ID', 'YOUR_API_HASH', and 'YOUR_PHONE_NUMBER'
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'
channel_id = '-1002235691978'  # Replace with your channel ID

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Connect to the client
    await client.start(phone_number)

    # Get the channel by its ID
    channel = PeerChannel(int(channel_id))

    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        print(event.message.message)

    # Keep the client running to listen for new messages
    await client.run_until_disconnected()

# Run the client
with client:
    client.loop.run_until_complete(main())
