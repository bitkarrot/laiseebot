# from requests.sessions import merge_setting
from labels import get_info_msgs, get_topmenu, get_lnaddress_info

from aiohttp.client import ClientSession
from supabase import create_client, Client
import os
from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet
from pylnbits.lnurl_p import LnurlPay

from local_config import LConfig
from client_methods import create_user, delete_user, get_user

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


async def bot_create_user(telegram_name):
    async with ClientSession() as session:
        wallet_config = await create_user(telegram_name, masterc, supabase, session)
        return wallet_config
        
async def bot_get_user(telegram_name):
    wallet_config = await get_user(telegram_name, masterc, supabase)
    return wallet_config


async def bot_delete_user(wallet_config):
    async with ClientSession() as session:
        del_result = await delete_user(wallet_config, masterc, supabase, session)
        print(f'Deletion result: {del_result}')
        return del_result


async def check_user_exists(username):
    # check if username exists in telegram
    from telethon.tl.functions.users import GetFullUserRequest
    try: 
        full = await client(GetFullUserRequest(username))
        print('telegram user check, should return same username')
        exists = full.user.username
        if username == exists:
            return True
        else: 
            return False
    except ValueError as e: 
        return e


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def alerthandler(event):
    sender = await event.get_sender()
    username = sender.username

    if username is None:
        msg = info['username']
        await event.reply(msg)
        return 1

    telegram_name = sender.username
    print(f'getting sender username: {telegram_name}')

    msg = info['welcome']
    await client.send_message(event.sender_id, msg, buttons=[
            [Button.text(menu['topup'], resize=True, single_use=False),
            Button.text(menu['send'], resize=True, single_use=False)],
            [Button.text(menu['balance'], resize=True, single_use=False),
            Button.text(menu['tools'], resize=True, single_use=False)], 
            [Button.text(menu['settings'], resize=True, single_use=False),
            Button.text(menu['help'], resize=True, single_use=False)]])
    # create or get user, return wallet_config
    wallet_config = await bot_create_user(telegram_name)

    # only use for testing
    userlink = await wallet_config.get_lnbits_link()
    await client.send_message(event.sender_id, userlink)
    

@client.on(events.CallbackQuery())
async def callback(event):
    sender = await event.get_sender()
    query_name = event.data.decode()
    print(f"callback: " + query_name)
    await event.edit('Thank you for clicking {}!'.format(query_name))
    telegram_name = str(sender.username)
    wallet_config = await bot_get_user(telegram_name)

    ### Top Up ###
    if query_name == 'Lightning Address':
        msg = "\n\nYour Lightning Address is <b> " + telegram_name + "@laisee.org</b> and is Case Sensitive. \n\n"
        msg = msg + "To check if the address is active: https://sendsats.to/qr/" + sender.username + "@laisee.org\n\n"
        msg = msg + ''.join(get_lnaddress_info(lang))
        await event.reply(msg)
    
    if query_name == 'QRCode':
        async with ClientSession() as session:
            lnurlp = LnurlPay(wallet_config, session)   
            body = {"description": "LN address for " + telegram_name,
                    "amount": 10,
                    "max": 10000,
                    "min": 10,
                    "comment_chars": 100}
            paylink = await lnurlp.create_paylink(body=body)
            print(str(paylink))
            msg = "Here is the Top Up QR Code and LNURL.\n\n"
            msg = msg +  f"<b>Min Deposit:</b> {paylink['min']} sats\n<b>Max Deposit:</b> {paylink['max']} sats\n" 
            lnurl = paylink['lnurl']
            msg = msg +  "\n\n" + lnurl
            await event.reply(msg)
        
    ### settings ###
    if query_name == 'Delete Wallet':
        msg = "OK, please give me a moment ....."
        await event.edit(msg)

        if wallet_config is not None:
            userlink = await wallet_config.get_lnbits_link()
            print(f'in Delete wallet, getting wallet config, lnbits link: {userlink}')
            result = await bot_delete_user(wallet_config)
            print(f'Result of deleting user: {result}')

            delete_msg = "OK, Deleted everything! Sorry to see you go. If you want to recreate your wallet anytime just type /start"
            await event.edit(delete_msg, buttons=[Button.text('Bye!', resize=True, single_use=True)])
        else: 
            delete_msg = "Having trouble deleting your wallet, please contact an admin via helpdesk"
            await event.edit(delete_msg)

    if query_name == 'Defund Wallet':
        # TODO create a lnurlw link + QR, if balance > 1
        msg = f"Withdraw entire balance from wallet"
        await event.reply(msg)

    ### send laisee ###
    if query_name == 'Telegram User':
        # TODO /send <amt> @username
        msg = "To send to another user, type `/send <<amt>> @username`"
        await event.reply(msg)

    if query_name == 'Laisee Image':
        # TODO user gives Amount, message
        msg = "clicked on 'Laisee Image' "
        await event.reply(msg)

    if query_name == 'Lnbits Url':
        link = await wallet_config.get_lnbits_link()
        msg = f"This is your link to the LNBits interface:\n {link}"
        await event.reply(msg)

    ###### Tools ######
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
    wallet_config = await bot_get_user(username)

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
        if wallet_config is not None:
            async with ClientSession() as session:
                user_wallet = UserWallet(config=wallet_config, session=session)
                walletinfo = await user_wallet.get_wallet_details()
                await client.send_message(event.sender_id, str(walletinfo))

                balance = float(walletinfo['balance'])/1000
                msg = f'Your Wallet Balance: {str(balance)} sats'
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


#### start bot ####
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
