# from requests.sessions import merge_setting
from labels import get_info_msgs, get_topmenu, get_lnaddress_info, en_laisee_created
from aiohttp.client import ClientSession
from supabase import create_client, Client
import os
from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet
from pylnbits.lnurl_p import LnurlPay
from pylnbits.lnurl_w import LnurlWithdraw

from local_config import LConfig
from client_methods import create_user, delete_user, get_user
from laisee_utils import get_QRimg, create_lnaddress, delete_lnaddress, create_laisee_qrcode
import datetime as dt

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
fee_base = 21
fee_percent = 0.01
template_file = 'templates/inlet_tiger_cut.svg'


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
            Button.text(menu['laisee'], resize=True, single_use=False)],
            [Button.text(menu['balance'], resize=True, single_use=False),
            Button.text(menu['send'], resize=True, single_use=False)], 
            [Button.text(menu['settings'], resize=True, single_use=False),
            Button.text(menu['tools'], resize=True, single_use=False)],
            [Button.text(menu['help'], resize=True, single_use=False)]])
    # create or get user, return wallet_config
    wallet_config = await bot_create_user(telegram_name)

    # only use for testing
    userlink = await wallet_config.get_lnbits_link()
    await client.send_message(event.sender_id, userlink)

    # Create lightning address
    async with ClientSession() as session:
        lnresult = await create_lnaddress(session, wallet_config)
        await client.send_message(event.sender_id, f"Lightning Address creation result: { lnresult }")

    print('>>>>> End of Start method <<<<<<<')

    

@client.on(events.CallbackQuery())
async def callback(event):
    sender = await event.get_sender()
    query_name = event.data.decode()
    print(f"callback: " + query_name)
    await event.edit('Thank you for clicking on {}!'.format(query_name))
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
            # print(str(paylink))
            msg = "Here is the Top Up QR Code and LNURL.\n\n"
            msg = msg +  f"<b>Min Deposit:</b> {paylink['min']} sats\n<b>Max Deposit:</b> {paylink['max']} sats\n" 
            lnurl = paylink['lnurl']
            qrimg = get_QRimg(telegram_name, lnurl)
            msg = msg +  "\n" + "<b>Scan me to deposit!</b>"
            await event.reply(msg)
            # print(qrimg)
            await client.send_file(event.chat_id, qrimg, caption=lnurl)
            #await client.send_file(event.chat_id, qrimg)

    
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
            # TODO delete lnaddress
        else: 
            delete_msg = "Having trouble deleting your wallet, please contact an admin via helpdesk"
            await event.edit(delete_msg)

    if query_name == 'Defund Wallet':
        # creates a lnurlw link + QR, if balance > 1
        async with ClientSession() as session:
            user_wallet = UserWallet(config=wallet_config, session=session)
            walletinfo = await user_wallet.get_wallet_details()
            balance = float(walletinfo['balance'])/1000
            fee_min = 1
            if balance > fee_min: # assume min for fees is 1
                body = {"title": "WithdrawLink", "min_withdrawable": 1, 
                "max_withdrawable": int(balance-fee_min), "uses": 1,
                "wait_time":1, "is_unique": True}
                withdraw = LnurlWithdraw(wallet_config, session)
                res = await withdraw.create_withdrawlink(body)
                # print(res)
                withdraw_id = res['id']
                link = wallet_config.lnbits_url + "/withdraw/" + withdraw_id
                msg = f"Here is your withdraw link: {link}"
                await event.reply(msg)
                # TODO convert SVG to PNG for telegram delivery
                svgimg = await withdraw.get_image_embed(withdraw_id)
                # print("\n\nSVG image: ", str(svgimg), "\n\n")
            else: 
                msg = f'Balance is too small to create a withdraw link'
                await event.reply(msg)



    laisee_amts = ['168', '1000', '8888', '25000']
    if query_name in laisee_amts: 
        msg = f'Ok, I will make a Laisee with {query_name} sats'
        await event.reply(msg)
        # todo: // add query to /laisee amt
        

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
        
    logger.info('Callback method called')



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

    ### send laisee ###
    if menu['send'] == input:
        # /send amount @username
        msg = info['send_detail']
        await event.reply(msg)
    
    ### make laisee image that is forwardable ### 
    if  menu['laisee'] == input:
        msg = info['laisee_amts']
        amts = menu['laisee_amts']
        amt_buttons = get_buttons(amts)
        amt_split = split(amt_buttons, 2)
        await client.send_message(event.sender_id, msg, buttons=amt_split)


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

    if ('/laisee' in input):
        await client.send_message(event.sender_id, f'Okay, give a moment to process this....')
        # create image w/lnurlw
        params = input.split(' ')
        if len(params) == 2:
            print(params[1])
            amt = int(params[1])
            fee_amt = int(amt * fee_percent) + fee_base
            send_amt = amt + fee_amt
            async with ClientSession() as session:
                lw = LnurlWithdraw(wallet_config, session)
                # creates link, doesn't check balance
                # must be of integer type
                title = f'Laisee amount: {int(send_amt)}'
                body = {"title": title, 
                    "min_withdrawable": int(send_amt),
                    "max_withdrawable": int(send_amt), 
                    "uses": 1, 
                    "wait_time": 3600, 
                    "is_unique": True }
                newlink = await lw.create_withdrawlink(body)
                print(f"create withdraw link with body: {body}, result link: {newlink} \n")
                withdraw_id = newlink['id']
                lnurl = newlink['lnurl']
                # always expires 3 months from now
                expires = str(dt.datetime.now() + dt.timedelta(days=365.25/4)).split(' ')[0]
                output_png = create_laisee_qrcode(lnurl, withdraw_id, expires, str(amt), template_file)
                await client.send_file(event.sender_id, output_png)
                await client.send_message(event.sender_id, en_laisee_created)
        else: 
            msg = "Looks like there isn't an amount or sufficient balance to send\n"
            msg = msg + "\nExample: <b>/laisee 100 </b>"
            await event.reply(msg)



    if ('/send' in input):
        await client.send_message(event.sender_id, f'Okay, give a moment to process this....')
        params = input.split(' ')
        if len(params) == 3:
            print(params[1], params[2])
            amt = float(params[1])
            receiver = params[2].split('@')[1]
            print(receiver)   
            # check if user exists
            try:
                recv_id = await client.get_peer_id(receiver)
                print(f'peer user id : {recv_id}')
                print(f'sender id : { event.sender_id }')
            except ValueError as e: 
                print(e)
                await client.send_message(event.sender_id, f'Not a valid Telegram User. @{receiver}')
                return
            # get receiver wallet config
            receiver_config = await bot_get_user(receiver)
            async with ClientSession() as session:
                recv_wallet = UserWallet(config=receiver_config, session=session)
                bolt11 = await recv_wallet.create_invoice(direction=False, amt=amt, memo="laisee", webhook="")
                send_wallet = UserWallet(config=wallet_config, session=session)
                # CHECK FOR SUFFICIENT BALANCE ERRORS
                # {"id": <string>, "name": <string>, "balance": <int>}
                sendinfo = await send_wallet.get_wallet_details()
                balance = float(sendinfo['balance'])/1000                
                fee_amt = int(amt * fee_percent) + fee_base
                if balance-fee_amt < amt:
                    await client.send_message(event.send_id, f'insufficient balance to send: {balance}')
                    return
                # send pay invoice
                payhash = await send_wallet.pay_invoice(direction=True, bolt11=bolt11)
                print(f'>>>>> payhash : {payhash}')
                inv_check = send_wallet.check_invoice(payhash)
                # notify sender and recipient
                if inv_check['paid']:
                    await client.send_file(recv_id, './images/honeybadger.jpeg')
                    await client.send_message(recv_id, f" Kung Hei Fat Choy! You've received a laisee from @{username}\n")
                    recvinfo = await recv_wallet.get_wallet_details()
                    await client.send_message(recv_id, str(recvinfo))

                    await client.send_message(event.sender_id, f'Sent Laisee to your recipient! @{receiver}')
                    sendinfo = await send_wallet.get_wallet_details()
                    await client.send_message(event.sender_id, str(sendinfo))
                else: 
                    await client.send_message(event.sender_id, "Error sending Laisee")

        else:
            msg = "Looks like there isn't enough info to send, please give an amount and a recipient\n"
            msg = msg + "\nExample: <b>/send 100 @username</b>"
            await event.reply(msg)


#### start bot ####
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)

    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
