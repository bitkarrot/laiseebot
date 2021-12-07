from telethon import TelegramClient, events, Button
import yaml


path  = "./"
config_file = path + 'config.yml'
with open(config_file, 'rb') as f:
    config = yaml.safe_load(f)
f.close()
TOKEN = config['bot_token']
print(f'Bot Token: {TOKEN}')

client = TelegramClient(config["session_name"],
                        config["api_id"],
                        config["api_hash"])

client.parse_mode = 'html'


@client.on(events.CallbackQuery())
async def callback(event):
    sender = await event.get_sender()
    query_name = event.data.decode()
    print(f"callback: " + query_name)
    await event.edit('Thank you for clicking {}!'.format(query_name))
    telegram_name = str(sender.username)
    await client.send_message(event.sender_id, f"Hello Hello {telegram_name}")


async def main():
    me = await client.get_me()
    username = me.username
    print(username)

    message = await  client.send_message(
        username,
        'This message has **bold**, `code`, __italics__ and '
        'a [nice website](https://example.com)!',
        link_preview=False)

    client.send_message(username, 'Hello!',
                        buttons=Button.inline('Click me', callback))

    
#### start bot ####
#client.start(bot_token=TOKEN)

with client:
    client.loop.run_until_complete(main())
    print('(Press Ctrl+C to stop this)')
    #    client.add_event_handler(handler)
    #    client.run_until_disconnected()
