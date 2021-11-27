# from requests.sessions import merge_setting
from labels import get_info_msgs, get_topmenu
from constants import core_currency

from telethon import TelegramClient, events, Button
import yaml
import logging
from logging import handlers
from coingecko_ticker import get_btcrates, sats_convert
from tg_utils import get_buttons, split

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)

bot_commands = ["<b>/balance</b> \t\t - gets wallet balance\n",
                "<b>/topup </b> \t\t - top up wallet",
                "<b>/send </b> - options to send sats\t\t",
                "<b>/rates</b> \t\t - Get latest BTC to Fiat Rates from Coingecko\n",
                "<b>/withdraw</b> \t\t - withdraw funds to external wallet\n", 
                "<b>/lnbits </b> \t\t - fetches the lnbits link to your account"
                "<b>/help</b> \t\t - Prints this list. \n\n"]

cmds = "".join(bot_commands)
help_msg = "Here are my commands: \n\n" + cmds
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

global_lang = 'en'
info = get_info_msgs(global_lang)
menu = get_topmenu(global_lang)


@client.on(events.NewMessage(pattern='(?i)/start', forwards=False, outgoing=False))
async def alerthandler(event):
    sender = await event.get_sender()
    print(sender)
    print(f'getting sender username: {sender.username}')

    msg = info['welcome']
    await client.send_message(event.sender_id, msg, buttons=[
            [Button.text(menu['topup'], resize=True, single_use=True),
            Button.text(menu['send'], resize=True, single_use=True)],
            [Button.text(menu['balance'], resize=True, single_use=True),
            Button.text(menu['tools'], resize=True, single_use=True)], 
            [Button.text(menu['settings'], resize=True, single_use=True),
            Button.text(menu['help'], resize=True, single_use=True)],])
    

@client.on(events.CallbackQuery())
async def callback(event):

    query_name = event.data.decode()
    print(f"callback: " + query_name)
    await event.edit('Thank you for clicking {}!'.format(query_name))

    ###### Tools ######
    rates = menu['toolopts'][0]
    if rates == query_name:
        msg = get_btcrates()
        await event.reply(msg)
    convert = menu['toolopts'][1]
    if convert == query_name:
        msg = sats_convert(query_name)
        await event.reply(msg)

    setlang = menu['toolopts'][2] # todo toggle global language
    if setlang == query_name:
        await event.reply(setlang)
        

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


    #################################### 

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



@client.on(events.NewMessage(pattern='(?i)/quit', forwards=False, outgoing=False))
async def alerthandler(event):
    sender = await event.get_sender()
    print(f'getting sender username: {sender.username}')
    await client.delete_dialog(sender.username)



#### start bot ####
client.start(bot_token=TOKEN)

with client:
    client.add_event_handler(handler)
    logger.info('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
