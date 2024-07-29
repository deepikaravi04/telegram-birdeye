from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel, Channel

# Replace 'API_ID', 'API_HASH', and 'PHONE_NUMBER' with your values
api_id = '21508194'
api_hash = 'd5779f0170e80a64dd902bfad2751cf1'
phone_number = '+919488223505'

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start(phone_number)

    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, Channel):
            print(f"Channel Name: {entity.title}")
            print(f"Channel ID: {entity.id}")
            print("="*50)

with client:
    client.loop.run_until_complete(main())
