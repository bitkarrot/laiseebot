# from requests.sessions import merge_setting
from labels import get_info_msgs, get_topmenu, lightning_address_info

from aiohttp.client import ClientSession
from local_config import LConfig
from supabase import create_client, Client
import os
from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet
from client_methods import create_user, delete_user, get_balance

from telethon import TelegramClient, events, Button

import yaml
import logging
from logging import handlers
from coingecko_ticker import get_btcrates, sats_convert
from tg_utils import get_buttons, split
from constants import core_currency

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)

############# logfile ############
level = logging.INFO
logger.setLevel(level)
log_path = "./logfile"
h = logging.handlers.RotatingFileHandler(log_path, encoding='utf-8', maxBytes=5 * 1024 * 1024, backupCount=5)
h.setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s:%(message)s"))
h.setLevel(level)
logger.addHandler(h)
###################################

path  = "./"
config_file = path + 'config.yml'
with open(config_file, 'rb') as f:
    config = yaml.safe_load(f)
f.close()


TOKEN = config['bot_token']
logger.info(f'Bot Token: {TOKEN}')

client = TelegramClient(config["session_name"],
                        config["api_id"],
                        config["api_hash"])

# Default to another parse mode
client.parse_mode = 'html'

lang = 'en'
info = get_info_msgs(lang)
menu = get_topmenu(lang)


masterc = Config(config_file="config.yml")
supa_url: str = os.environ.get("SUPABASE_URL")
supa_key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supa_url, supa_key)
wallet_config = masterc # initial config


async def get_user(telegram_name):
    async with ClientSession() as session:
        wallet_config = await create_user(telegram_name, masterc, supabase, session)
        return wallet_config

async def del_user(wallet_config):
    async with ClientSession() as session:
        del_result = await delete_user(wallet_config, masterc, supabase, session)
        print(f'Deletion result: {del_result}')


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def alerthandler(event):
    sender = await event.get_sender()
    print(sender)
    telegram_name = sender.username
    print(f'getting sender username: {telegram_name}')

    msg = info['welcome']
    await client.send_message(event.sender_id, msg, buttons=[
            [Button.text(menu['topup'], resize=True, single_use=True),
            Button.text(menu['send'], resize=True, single_use=True)],
            [Button.text(menu['balance'], resize=True, single_use=True),
            Button.text(menu['tools'], resize=True, single_use=True)], 
            [Button.text(menu['settings'], resize=True, single_use=True),
            Button.text(menu['help'], resize=True, single_use=True)],])
    
    # create or get user, return wallet_config
    

@client.on(events.CallbackQuery())
async def callback(event):
    sender = await event.get_sender()
    query_name = event.data.decode()
    print(f"callback: " + query_name)
    await event.edit('Thank you for clicking {}!'.format(query_name))

    lang = 'en'
    menu = get_topmenu(lang)

    ### Top Up ###
    if query_name == 'Lightning Address':
        msg = "\n\nYour Lightning Address is <b> " + str(sender.username) + "@laisee.org</b> and is Case Sensitive. \n\n"
        msg = msg + "To check if the address is active: https://sendsats.to/qr/" + sender.username + "@laisee.org\n\n"
        msg = msg + ''.join(lightning_address_info)
        await event.reply(msg)
    
    if query_name == 'QR Code':
        msg = 'qr code'
        await event.reply(msg)
    
    if query_name == 'LNURL':
        msg = 'lnurl'
        await event.reply(msg)


    ### settings ###
    if query_name == 'Delete Wallet':
        delete_msg = "OK, Deleting everything! Sorry to see you go. If you want to recreate your wallet anytime just type /start"
        await event.edit(delete_msg, buttons=[Button.text('Bye!', resize=True, single_use=True)])
        
    if query_name == 'Lnbits Url':
        msg = "clicked on lnbits url"
        await event.reply(msg)

    if query_name == 'Withdraw':
        msg = "clicked on withdraw"
        await event.reply(msg)

    ### send laisee ###
    if query_name == 'Telegram User':
        msg = "clicked on Telegram User "
        await event.reply(msg)

    if query_name == 'Image':
        msg = "clicked on 'Image' "
        await event.reply(msg)

    if query_name == 'Print Bulk QR':
        msg = "clicked on 'Bulk QR' "
        await event.reply(msg)



    ###### Tools ######
    # print(menu['toolopts'])
    rates = menu['toolopts'][0]
    if rates == query_name:
        msg = get_btcrates()
        await event.reply(msg)

    convert = menu['toolopts'][1]
    if convert == query_name:
        msg = sats_convert(query_name)
        await event.reply(msg)
        

@events.register(events.NewMessage(incoming=True, outgoing=False))
async def handler(event):

    input = str(event.raw_text)
    sender = await event.get_sender()
    username = sender.username
    chatid = event.chat_id
    logger.info(f"handler: {input}, by @{username} in chatid: {chatid}")
        
    if username is None:
        msg = info['username']
        await event.reply(msg)
        return 1

    if menu['topup'] == input:
        msg =  info['topup']
        topup = menu['topopts']
        topup_buttons = get_buttons(topup)
        topupsplit = split(topup_buttons, 1)
        await client.send_message(event.sender_id, msg, buttons=topupsplit)

    if menu['settings'] == input:
        msg = info['settings']
        settings = menu['setopts']
        set_buttons = get_buttons(settings)
        set_split = split(set_buttons, 1)
        await client.send_message(event.sender_id, msg, buttons=set_split)

    if menu['send'] == input: 
        msg = info['send']
        send_options = menu['sendopts']
        send_buttons = get_buttons(send_options)
        send_split = split(send_buttons, 1)

        await client.send_message(event.sender_id, msg, buttons=send_split)

    if menu['balance'] == input:
        msg = info['wallet']
        await client.send_message(event.sender_id, msg)


    ##### Help , Tools ############

    if menu['help'] == input:
        msg = info['help']
        await client.send_message(event.sender_id, msg)

    if menu['tools'] == input:
        msg = info['tools']
        tool_options = menu['toolopts']
        tool_buttons = get_buttons(tool_options)
        tool_split = split(tool_buttons, 1)
        await client.send_message(event.sender_id, msg, buttons=tool_split)

    if ('/btc' in input) or ('/sats' in input) or ('/fiat' in input): 
        msg = sats_convert(input)
        await event.reply(msg)


'''
@client.on(events.NewMessage(pattern='/quit', forwards=False, outgoing=False))
async def alerthandler(event):
    sender = await event.get_sender()
    print(f'getting sender username: {sender.username}')
    msg = " Ok Bye!"
    await event.edit(msg, buttons=[ Button.text(menu['help'], resize=True, single_use=True)])
'''


#### start bot ####
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
