# from requests.sessions import merge_setting
from labels import get_info_msgs, get_topmenu, get_lnaddress_info, en_laisee_created, get_help_info
from aiohttp.client import ClientSession
from supabase import create_client, Client
from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet
from pylnbits.lnurl_p import LnurlPay
from pylnbits.lnurl_w import LnurlWithdraw

from local_config import LConfig
from client_methods import create_user, delete_user, get_user
from laisee_utils import get_QRimg, create_lnaddress, delete_lnaddress, create_laisee_qrcode, convertSVG
import datetime as dt
import json
import time

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
helpinfo = get_help_info(lang)

masterc = Config(config_file="config.yml")
supa_url: str = config['SUPABASE_URL'] 
supa_key: str = config['SUPABASE_KEY'] 
passkey: str = config['PASSKEY'] # temporary fix for supabase for now


supabase: Client = create_client(supa_url, supa_key)
fee_base = 0
fee_percent = 0
template_file = 'templates/inlet_tiger_cut.svg'


async def bot_create_user(telegram_name):
    async with ClientSession() as session:
        wallet_config = await create_user(telegram_name, masterc, supabase, session, passkey)
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
        logger.info(str(e))
        return e


async def QR_Topup(wallet_config):
    async with ClientSession() as session:
        lnurlp = LnurlPay(wallet_config, session)
        paylinks = await lnurlp.list_paylinks()
        print(f'paylinks: {paylinks}')
        link = None
        for i in paylinks:
            if i['description'] == "QRCode":
                link = i
                print(f' fetched historical link')                
        if link is None:
            # if no qr paylink then create one
            body = {"description": "QRCode",
                    "amount": 10,
                    "max": 10000,
                    "min": 10,
                    "comment_chars": 100}
            link = await lnurlp.create_paylink(body=body)
            print(f'created QRCODE lnurlp: {str(link)}')
        return link 


async def get_laisee_img(amt: int, wallet_config: str):
    status = await check_balance(wallet_config, amt)
    if status is True: 
        async with ClientSession() as session:
            lw = LnurlWithdraw(wallet_config, session)
            # creates link, doesn't check balance
            # must be of integer type
            title = f'Lightning Laisee: {int(amt)}'
            body = {"title": title, 
                "min_withdrawable": int(amt),
                "max_withdrawable": int(amt), 
                "uses": 1, 
                "wait_time": 1, 
                "is_unique": True }
            newlink = await lw.create_withdrawlink(body)
            print(f"create withdraw link with body: {body}, result link: {newlink} \n")
            withdraw_id = newlink['id']
            lnurl = newlink['lnurl']
            # always expires 3 months from now
            expires = str(dt.datetime.now() + dt.timedelta(days=365.25/4)).split(' ')[0]        
            output_png = create_laisee_qrcode(lnurl, withdraw_id, expires, str(amt), template_file)
            return output_png, withdraw_id
    else: 
        return None, 0


async def get_balance(session, wallet_config) -> float:
    user_wallet = UserWallet(config=wallet_config, session=session)
    walletinfo = await user_wallet.get_wallet_details()
    # await client.send_message(event.sender_id, str(walletinfo))
    balance = float(walletinfo['balance'])/1000
    return balance


async def defund_wallet(wallet_config):
    # creates a lnurlw link + QR, if balance > 1
    async with ClientSession() as session:
        user_wallet = UserWallet(config=wallet_config, session=session)
        walletinfo = await user_wallet.get_wallet_details()
        balance = float(walletinfo['balance'])/1000
        fee_min = -1
        if balance > fee_min: # assume min for fees is 1
            body = {"title": "WithdrawLink", "min_withdrawable": 1, 
            "max_withdrawable": int(balance-fee_min), "uses": 1,
            "wait_time":1, "is_unique": True}
            withdraw = LnurlWithdraw(wallet_config, session)
            res = await withdraw.create_withdrawlink(body)
            withdraw_id = res['id']
            svgimg = await withdraw.get_image_embed(withdraw_id)
            return withdraw_id, svgimg
        else: 
            return False, False


async def get_created_laisee(session, wallet_config):
    if wallet_config is not None:
        lw = LnurlWithdraw(wallet_config, session)
        links = await lw.list_withdrawlinks()
        total_laisee_amt = 0 
        entries = []
        for item in links: 
            if 'Laisee' in item['title']: 
                wtitle = item['title'] + " sats "
                wamt = item['max_withdrawable']
                total_laisee_amt += wamt
                wlink = wallet_config.lnbits_url + "/withdraw/" + item['id']
                wdate = dt.date.fromtimestamp(item['open_time'])
                # expires in 3 months from wdate
                from datetime import timedelta
                delta = timedelta(days=90)
                expiry = wdate + delta
                expiry_date = expiry.strftime("%A %d. %B %Y")
                entry = "<a href=\"" + wlink + "\">" + wtitle + "</a> expires: " + expiry_date
                entries.append(entry)
        return entries, total_laisee_amt
    else:
        return None, None


async def client_balance(wallet_config):
    async with ClientSession() as session:
        entries, total_laisee_amt = await get_created_laisee(session, wallet_config)
        balance = await get_balance(session, wallet_config)
        avail_balance  = balance  - total_laisee_amt

    msg = "Current Balance in Wallet: " + str(balance) + "\n"
    msg += "Total Amount Allocated to Laisee: " + str(total_laisee_amt) + "\n"
    msg += "<b>Available Balance for New Laisee: " + str(avail_balance) + "</b>\n\n"
    return msg, entries


async def check_balance(wallet_config, alloc_amt): 
    async with ClientSession() as session:
        entries, total_laisee_amt = await get_created_laisee(session, wallet_config)
        balance = await get_balance(session, wallet_config)
        avail_balance  = balance  - total_laisee_amt
        if alloc_amt > avail_balance + 1: 
            return False
        else: 
            return True 



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
    query = '/fiat 1 HKD'
    sats_msg = sats_convert(query)
    await client.send_message(event.sender_id, "1 HKD is currently worth " + sats_msg)
    # only use for testing
    userlink = await wallet_config.get_lnbits_link()
    # await client.send_message(event.sender_id, f'Link For Testing only: \n{userlink} \n\n <b>Testnet: Max Send and Receive is 500 sats (lnpay.co backend)</b> \n')

    # Create lightning address - first check does it exist for this wallet? 
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
            async with ClientSession() as session:
                status = await delete_lnaddress(session, wallet_config)
                print(f'Delete LN Address Status { status }')
        else: 
            delete_msg = "Having trouble deleting your wallet, please contact an admin via helpdesk"
            await event.edit(delete_msg)
    

    if query_name == 'Defund Wallet':
        withdraw_id, svgimg = await defund_wallet(wallet_config)
        if withdraw_id:
            link = wallet_config.lnbits_url + "/withdraw/" + withdraw_id
            # link points to QR Code
            msg = f"Here is your withdraw link: {link}"
            await event.reply(msg)
            pngfile = convertSVG(svgimg, withdraw_id)
            await client.send_file(event.sender_id, pngfile)
            # convert SVG to PNG for telegram delivery
        else: 
            async with ClientSession() as session:
                msg = f'Balance is too small to create a withdraw link'
                await event.reply(msg)
                balance = await get_balance(session, wallet_config)
                msg = f'Your Wallet Balance: {str(balance)} sats'
                await client.send_message(event.sender_id, msg)


    laisee_amts = ['168', '1000', '8888', '25000']
    if query_name in laisee_amts: 
        amt = query_name
        msg = f'Ok, I will make a Laisee with {amt} sats plus fees, please give me a moment...'
        await event.reply(msg)
        output_png, withdraw_id = await get_laisee_img(int(amt), wallet_config)
        if output_png is None:
            await client.send_message(event.sender_id, "Insufficient Balance available to create new laisee.")
            return
        # total = int(amt) + fee_amt
        await client.send_file(event.sender_id, output_png)
        await client.send_message(event.sender_id, en_laisee_created)
        withdraw_link =  masterc.lnbits_url + "/withdraw/" + withdraw_id
        await client.send_message(event.sender_id, "Backup link in case above image does not scan: " + withdraw_link)        

    if query_name == 'Lnbits Url':
        link = await wallet_config.get_lnbits_link()
        msg = f"This is your link to the LNBits interface:\n {link}"
        await event.reply(msg)

    if query_name == 'More Lightning Address Info': 
        msg = "\nTo check if the address is active: https://sendsats.to/qr/" + telegram_name + "@laisee.org\n\n"
        msg = ' '.join(get_lnaddress_info('en')) + msg
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
        link = await QR_Topup(wallet_config)
        msg = "There are 3 ways to top up your wallet:\n\n"
        msg += "1. Create a custom invoice amount via the /invoice command\n\n"
        msg += "2. Use a LNURL QR Code (see below)\n\n"
        msg += "3. A Lightning Address (see below)\n\n"
        msg += "=======================\n\n"
        msg += "Here is the Top Up QR Code and LNURL.\n\n"
        msg = msg +  f"<b>Min Deposit:</b> {link['min']} sats\n<b>Max Deposit:</b> {link['max']} sats\n" 
        lnurl = link['lnurl']
        qrimg = get_QRimg(username, lnurl)
        if type(qrimg) == str: 
            msg = msg +  "\n" + "<b>Scan me to deposit!</b>"
            await client.send_message(event.sender_id, msg)
            await client.send_file(event.chat_id, file=qrimg)
        await client.send_message(event.chat_id, lnurl)
        msg = "\n\nYour Lightning Address is <b> " + username + "@laisee.org</b> and is <b>Case Sensitive</b>. \n\n"
        msg = msg  + "If you just created your wallet, please wait a few minutes for the address to deploy\n"
        ln_info = "More Lightning Address Info"
        await client.send_message(event.sender_id, msg, buttons=Button.inline(ln_info,ln_info))
 


    if menu['settings'] == input:
        msg = info['settings']
        settings = menu['setopts']
        set_buttons = get_buttons(settings)
        msg_split = split(set_buttons, 1)
        await client.send_message(event.sender_id, msg, buttons=msg_split)

    ### send TG laisee ###
    if menu['send'] == input:
        # /send amount @username
        msg = info['send_detail']
        await event.reply(msg)

    
    ### make laisee image that is forwardable, buttons for amounts shown here ### 
    if  menu['laisee'] == input:
        msg = info['laisee_amts']
        amts = menu['laisee_amts']
        amt_buttons = get_buttons(amts)
        amt_split = split(amt_buttons, 4)
        await client.send_message(event.sender_id, msg, buttons=amt_split)

        msg, entries = await client_balance(wallet_config)
        await client.send_message(event.sender_id, msg)
        entry_msg = 'To see created laisee: `/entries`'
        await client.send_message(event.sender_id, entry_msg)


    if menu['balance'] == input:
        if wallet_config is not None:
            async with ClientSession() as session:
                msg, entries = await client_balance(wallet_config)
                await client.send_message(event.sender_id, msg)
                entry_msg = 'To see created laisee: `/entries`'
                await client.send_message(event.sender_id, entry_msg)



    ##### Help , Tools ############
    if menu['help'] == input:
        msg = info['help']
        await client.send_message(event.sender_id, msg)
        content = '<b>- How to Make Laisee</b>\n\n' + helpinfo['make'] + "\n\n"
        content += '<b>- Redeem Laisee</b>\n\n' + helpinfo['redeem'] + "\n\n"
        content += '<b>- Lightning Wallets</b>\n\n See https://laisee.org/wallets for more information \n\n'
        content += '<b>- Helpdesk:</b>\n\n Visit us at https://t.me/laiseehelpdesk\n\n'

        await client.send_message(event.sender_id, content)

    if menu['tools'] == input:
        msg = info['tools']
        tool_options = menu['toolopts']
        tool_buttons = get_buttons(tool_options)
        tool_split = split(tool_buttons, 1)
        await client.send_message(event.sender_id, msg, buttons=tool_split)

    if ('/btc' in input) or ('/sats' in input) or ('/fiat' in input): 
        msg = sats_convert(input)
        await event.reply(msg)


    if ('/balance' in input):
        if wallet_config is not None:
            async with ClientSession() as session:
                msg, entries = await client_balance(wallet_config)
                await client.send_message(event.sender_id, msg)
                entry_msg = 'To see created laisee: `/entries`'
                await client.send_message(event.sender_id, entry_msg)



    if ('/details' in input):
        msg, entries = await client_balance(wallet_config)
        await client.send_message(event.sender_id, msg)
        entry_msg = 'To see created laisee: `/entries`'
        await client.send_message(event.sender_id, entry_msg)


    if ('/entries' in input):
        async with ClientSession() as session:
            entries, total_laisee_amt = await get_created_laisee(session, wallet_config)
            for i in entries:
                await client.send_message(event.sender_id, i)
            totals = "Total Laisee Created:  " + str(len(entries))
            await client.send_message(event.sender_id, totals)
                


    if ('/laisee' in input):
        await client.send_message(event.sender_id, f'Okay, give me a moment to process this....')
        try:
            # create image w/lnurlw
            params = input.split(' ')
            if len(params) == 2:
                print(params[1])
                amt = int(params[1])
                output_png, withdraw_id = await get_laisee_img(amt, wallet_config)
                if output_png is None:
                    await client.send_message(event.sender_id, "Insufficient Balance available to create new laisee.")
                    return
                await client.send_file(event.sender_id, output_png)
                await client.send_message(event.sender_id, en_laisee_created)
                withdraw_link =  masterc.lnbits_url + "/withdraw/" + withdraw_id
                await client.send_message(event.sender_id, "Backup link in case above image does not scan: " + withdraw_link)

            else: 
                msg = "Looks like there isn't an amount or sufficient balance to send\n"
                msg = msg + "\nExample: <b>/laisee 100 </b>"
                await event.reply(msg)
        except Exception as e:
                print(e)
                msg = "Error creating laisee: " + str(e)
                await event.reply(msg)


    if ('/invoice' in input):            
            try:
                params = input.split(' ')
                if len(params) == 2:
                    print(params[1])
                    amt = int(params[1])
                    async with ClientSession() as session:
                        uw = UserWallet(config=wallet_config, session=session)
                        bolt11json = await uw.create_invoice(direction=False, amt=amt, memo="laisee invoice", webhook="https://laisee.org")
                        inv_content = json.dumps(bolt11json)
                        print(inv_content)

                        bolt11_inv = bolt11json['payment_request']
                        await client.send_message(event.sender_id, bolt11_inv)
                else: 
                    msg = "Looks like there isn't enough info to send, please give an amount to create an invoice\n"
                    msg = msg + "\nExample: <b>/invoice 100</b>"
                    await event.reply(msg)
            except Exception as e:
                logger.info("error creating invoice" + str(e))
                msg = "Error creating invoice: " + str(e)
                await event.reply(msg)



    if ('/send' in input):
        # TODO: factor out into separate method
        await client.send_message(event.sender_id, f'Okay, give me a moment to process this....')
        params = input.split(' ')
        if len(params) == 3:
            try:
                print(params[1], params[2])
                amt = float(params[1])
            except ValueError as e: 
                await client.send_message(event.sender_id, f'Not a valid amount')
                return
            try:
                receiver = params[2].split('@')[1]
                print(receiver)   
                # check if user exists
                recv_id = await client.get_peer_id(receiver)
                print(f'peer user id : {recv_id}')
                print(f'sender id : { event.sender_id }')
                # get receiver wallet config
                receiver_config = await bot_get_user(receiver)
                print(f'receiver_config: {receiver_config}')
                if receiver_config is None:
                    raise Exception("No conversation yet")

            except ValueError as e: 
                print(e)
                await client.send_message(event.sender_id, f'Not a valid Telegram User. @{receiver}')
                return
            except IndexError as e: 
                await client.send_message(event.sender_id, f'Invalid format. Here is an Example: <b>/send 100 @username</b>" ')
                return
            except Exception as e: 
                await client.send_message(event.sender_id, f' This user has not started a conversation yet with @laiseebot')
                return

            try: 
                async with ClientSession() as session:
                    recv_wallet = UserWallet(config=receiver_config, session=session)
                    recvwallet = await recv_wallet.get_wallet_details()
                    print(f"recvr wallet info : {recvwallet}")

                    bolt11 = await recv_wallet.create_invoice(direction=False, amt=int(amt), memo="laisee", webhook="https://laisee.org")
                    send_wallet = UserWallet(config=wallet_config, session=session)

                    # CHECK FOR INSUFFICIENT BALANCE ERRORS
                    # {"id": <string>, "name": <string>, "balance": <int>}
                    sendinfo = await send_wallet.get_wallet_details()
                    balance = float(sendinfo['balance'])/1000                
                    fee_amt = 1 # int(amt * fee_percent) + fee_base
                    if balance-fee_amt < amt:
                        await client.send_message(event.sender_id, f'insufficient balance to send: {balance}, fee amount: {fee_amt}')
                        return
                    
                    # send pay invoice
                    payhash = await send_wallet.pay_invoice(direction=True, bolt11=bolt11['payment_request'])
                    # print(f'>>>>> payhash : {payhash}')
                    payment_hash = "/"+payhash['payment_hash']   # TODO Fix missing "/" bug in pylnbits 
                    #print(f'paymenthash: {payment_hash} ')
                    inv_check = await send_wallet.check_invoice(payment_hash)
                    inv_content = json.dumps(inv_check)
                    print(f'inv check: {inv_content}')
                    
                    # notify sender and recipient
                    if inv_check['paid']:
                        await client.send_file(recv_id, './images/laisee.png')
                        await client.send_message(recv_id, f" Kung Hei Fat Choy! You've received a laisee from @{username} for {amt} sats.\n")
                        recvinfo = await recv_wallet.get_wallet_details()
                        await client.send_message(recv_id, str(recvinfo))

                        await client.send_message(event.sender_id, f'Sent Laisee to your recipient! @{receiver}')
                        sendinfo = await send_wallet.get_wallet_details()
                        await client.send_message(event.sender_id, str(sendinfo))
                    else: 
                        await client.send_message(event.sender_id, "Error sending Laisee")

            except Exception as e: 
                logger.info("in /send: " + str(e))
                # await client.send_message(event.sender_id, str(e))
                if 'message' in bolt11: # error can't get bolt11
                    await client.send_message(event.sender_id, bolt11['message'])
                    print(f'bolt11: {bolt11}')
                    return
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
