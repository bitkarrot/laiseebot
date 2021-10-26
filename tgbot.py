# from requests.sessions import merge_setting
from telethon import TelegramClient, events, Button
import yaml
import logging
from logging import handlers
import datetime as dt
from coingecko_ticker import get_btcrates, sats_convert
from constants import core_currency

import os
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)

bot_commands = ["<b>/btc</b> \t\t - Ex: /btc 0.04 USD\n",
                "<b>/rates</b> \t\t - Get latest BTC to Fiat Rates from Coingecko\n",
                "<b>/helpme</b> \t\t - Prints this list. \n\n"]

cmds = "".join(bot_commands)
help_msg = "Here are the commands I currently am enslaved to: \n\n" + cmds
header_msg = '<b>Lightning Laisee</b>\n\n'
intro = header_msg + help_msg

path  = "./"
config_file = path + 'config.yml'
with open(config_file, 'rb') as f:
    config = yaml.safe_load(f)
f.close()


############# logfile ############
level = logging.INFO
logger.setLevel(level)
log_path = path + "logfile"
h = logging.handlers.RotatingFileHandler(log_path, encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=5)
h.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s:%(message)s"))
h.setLevel(level)
logger.addHandler(h)

###################################

TOKEN = config['bot_token']
logger.info(f'Bot Token: {TOKEN}')

client = TelegramClient(config["session_name"],
                        config["api_id"],
                        config["api_hash"])

# Default to another parse mode
client.parse_mode = 'html'

@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def new_handler(event):
    await event.reply('Hi! Go to /helpme for instructions')


@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):
    input = str(event.raw_text)
    sender = await event.get_sender()
    username = sender.username
    rawtext = event.raw_text
    chatid = event.chat_id
    logger.info(f"handler: {input}, by @{username} in chatid: {chatid}")
    
    '''
    if chatid != allowed_chatrooms:
        msg = 'Sorry you are not part of the club! Please join the chatroom to use.'
        await event.reply(msg)
        return 1
    '''
    
    if username is None:
        msg = 'Please set a username in telegram in order use this bot.'
        await event.reply(msg)
        return 1

    if '/helpme' in rawtext:
        await event.reply(intro)
        
    if '/rates' in rawtext:
        msg = get_btcrates()
        await event.reply(msg)
    
    if '/btc' in rawtext:
        msg = sats_convert(rawtext)
        await event.reply(msg)    
    

#### start bot ####
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
