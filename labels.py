
en_menu = {'topup':'Top Up Wallet', 
            'send': 'Send Laisee',
            'balance': 'Get Balance',
            'settings': 'Settings',
            'tools': 'Tools',
            'help': 'Help', 
            'lang': 'Toggle 中文',
            'topopts': ['Lightning Address', 'QR Code', 'LNURL'], 
            'setopts': ['Lnbits Url', 'Withdraw', 'Delete Wallet'],
            'sendopts': ['Telegram User', 'Image', 'Print Bulk QR'], 
            'toolopts': ['Get Rates','Convert $₿⚡️'] }

cn_menu = {'topup':'充值余额', 
            'send': '送红包',
            'balance': '账户余额',
            'settings': '帐号设定',
            'tools': '工具',
            'help': '得到帮助', 
            'lang': '切换 En',
            'topopts': ['Lightning Address', 'QR Code', 'LNURL'], 
            'setopts': ['Lnbits Url', 'Withdraw', 'Delete Wallet'],
            'sendopts': ['Telegram User', 'Image', 'Print Bulk QR'], 
            'toolopts': ['Get Rates','Convert $₿⚡️']  }

en_info = {'help': "<< Help message here >>\n\n<< add link to Telegram Help chatroom>> ",
           'tools': "Useful Tools\n\n << Add message to explain Tools here >> \n\n",
           'send': "How to Send Laisee\n\n << Add message to explain Send Options here >> \n\n",
           'settings': "<b> Settings </b> \n\n << add good settings message here>> \n\n\n",
           'topup': "<b> Top Up Options</b> \n\n << add good explanation message here>> \n\n\n",
           'username': 'Please set a username in telegram in order use this bot.',
           'welcome': 'Welcome to Lightning Laisee\n\n << add detailed welcome message here >> \n',
           'wallet':  "Your Wallet Balance\n",
           }

cn_info = {'help': "<< Help message here >>\n\n<< add link to Telegram Help chatroom>> ",
           'tools': "Useful Tools\n\n << Add message to explain Tools here >> \n\n",
           'send': "How to Send Laisee\n\n << Add message to explain Send Options here >> \n\n",
           'settings': "<b> Settings </b> \n\n << add good settings message here>> \n\n\n",
           'topup': "<b> Top Up Options</b> \n\n << add good explanation message here>> \n\n\n",
           'username': 'Please set a username in telegram in order use this bot.',
           'welcome': 'Welcome to Lightning Laisee\n\n << add detailed welcome message here >> \n',
           'wallet':  "Your Wallet Balance\n",
           }


en_LNaddress_info = [ "With a Lightning Address you can send sats to this wallet from another service, such as @lntxbot or a lightning enabled wallet. \n\n\n ",
                    "Top Up Example: /send 1000  username@laisee.org \n\n\n", 
                    "This Lightning Address is currently set to accept between <b> 10 to 10,000 sats maximum in a transaction. </b>\n\n",
                    "If you just created your wallet, please wait a few minutes for the address to deploy. ",
                    " If your address is active, you should see a QR code when visiting the above link. It may also be visible here as a QR preview. \n\n",
                    "If you are having trouble accessing the address, please visit the helpdesk.", 
                    " For more information about Lightning Addresses, please visit lightningaddress.com \n\n "]

cn_LNaddress_info = [ "With a Lightning Address you can send sats to this wallet from another service, such as @lntxbot or a lightning enabled wallet. \n\n\n ",
                    "Top Up Example: /send 1000  username@laisee.org \n\n\n", 
                    "This Lightning Address is currently set to accept between <b> 10 to 10,000 sats maximum in a transaction. </b>\n\n",
                    "If you just created your wallet, please wait a few minutes for the address to deploy. ",
                    " If your address is active, you should see a QR code when visiting the above link. It may also be visible here as a QR preview. \n\n",
                    "If you are having trouble accessing the address, please visit the helpdesk.", 
                    " For more information about Lightning Addresses, please visit lightningaddress.com \n\n "]


# Top Menu Buttons
def get_topmenu(lang):
    if lang == 'en':
        return en_menu
    elif lang =='cn': 
        return cn_menu

# get informative messages 
def get_info_msgs(lang):
    if lang == 'en':
        return en_info
    elif lang == 'cn':
        return cn_info

def get_lnaddress_info(lang):
    if lang == 'en':
            return en_LNaddress_info
    elif lang =='cn': 
        return cn_LNaddress_info

