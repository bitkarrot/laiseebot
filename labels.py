
en_menu = {'topup':'Top Up Wallet', 
            'laisee': 'Create Laisee',
            'send': 'Send Laisee via Telegram',
            'balance': 'Get Balance',
            'settings': 'Settings',
            'tools': 'Tools',
            'help': 'Help', 
            'lang': 'Toggle 中文',
            'topopts': ['Lightning Address', 'QRCode'], 
           # 'setopts': ['Defund Wallet','Lnbits Url', 'Delete Wallet'],
            'setopts': ['Defund Wallet','Lnbits Url'],
            'sendopts': ['Telegram User', 'Laisee Image'], 
            'toolopts': ['Get Rates','Convert $₿⚡️'], 
            'laisee_amts': ['168', '1000', '8888', '25000'] }


en_info = {'help': "Need help making, redeeming or understanding Laisee? We got you covered!\n\n",
           'tools': "Get the latest bitcoin prices and quickly convert between bitcoin, dollars and other currencies.",
           'send': "How to Send Laisee\n\n << Add message to explain Send Options here >> \n\n",
           'settings': "Click below to withdraw your remaining balance or obtain your LNBits URL.\n\nDon't forget to leave enough funds in your wallet for Laisee that have not been redeemed yet!",
           'topup': "There are multiple ways you can add funds to your wallet. \n Scan the QR code below with a wallet that supports LNURL, or copy/paste the LNURL below. \n You may also send funds to your Lightning Address directly, or pass your Lightning Address to others. You can also create a classic Lightning invoice with the command /invoice < amount >",
           'username': "Please set a username in telegram in order use this bot. Sorry about that.",
           'welcome': "Welcome to Lightning Laisee!\n\nLaisee are little red envelopes with money. Like traditional red pockets, Lightning Laisee contain money that you can gift to others. Lightning Laisee contain satoshi, the smallest unit of a bitcoin. 1 Hong Kong dollar is currently worth 0.00000266 bitcoin, or 266 satoshi.\n\nYou can send Lightning Laisee to anyone on the globe.\nTo start, deposit funds into your wallet, then create a Laisee.",
           'wallet':  "Your Wallet Balance\n",
           'laisee_amts': "Tell us how much you want to send by selecting an option below.\nBe sure to have enough balance! Or, customize: `/laisee  < amount > ",
           'send_detail': "To send to another user, type in the message box:\n/send amt @username \n\nFor Example: /send 100 @laiseebot"
           }


en_LNaddress_info = [ "A Lightning Address looks like an email address, but it can be used to send funds to your Laisee Bot account from any external wallet that supports it.\n\n This Lightning Address is set to accept between 10 and 10,000 satoshi per transaction. You can use your Lightning Address as often as you like. If your Laisee Bot account is new, you may need to wait a few minutes before your Lightning Address is active.\n\n",
                    "Top Up Example from @lntxbot: /send 1000 laiseebot@laisee.org \n\n", 
                    "This Lightning Address is currently set to accept between <b> 10 to 10,000 sats maximum in a transaction. </b>\n\n",
                    "If you just created your wallet, please wait a few minutes for the address to deploy. ",
                    "If you are having trouble accessing the Lightning address, please visit the helpdesk."]



en_send_created = "Okay, I’m going to create a Laisee over < amount > satoshi. Please hodl on a moment…"
en_laisee_created =  "Congrats, here is your Laisee! You can forward this to anyone you like, save it to your device, attach it to an email or print it out. If you need, you can share with the recipient how the laisee can be redeemed, with this link: https://laisee.org/posts/redeem \n\nRemember to keep enough funds in your wallet!"


en_help = {	'make' : 'See https://laisee.org/posts/send',
    		'wallets' : 'See https://laisee.org/posts/wallets',
		    'redeem' : 'See https://laisee.org/posts/redeem'
            }		
		
# Top Menu Buttons
def get_topmenu(lang):
    if lang == 'en':
        return en_menu

# get informative messages 
def get_info_msgs(lang):
    if lang == 'en':
        return en_info

def get_lnaddress_info(lang):
    if lang == 'en':
        return en_LNaddress_info

def get_help_info(lang):
    if lang == 'en':
        return en_help