
en_menu = {'topup':'Top Up Wallet', 
            'laisee': 'Create Laisee',
            'send': 'Send Laisee via Telegram',
            'balance': 'Get Balance',
            'settings': 'Settings',
            'tools': 'Tools',
            'help': 'Help', 
            'lang': 'Toggle 中文',
            'topopts': ['Lightning Address', 'QRCode'], 
            'setopts': ['Defund Wallet','Lnbits Url', 'Delete Wallet'],
            'sendopts': ['Telegram User', 'Laisee Image'], 
            'toolopts': ['Get Rates','Convert $₿⚡️'], 
            'laisee_amts': ['168', '1000', '8888', '25000'] }


en_info = {'help': "<< Help message here >>\n\n<< add link to Telegram Help chatroom>> ",
           'tools': "Useful Tools\n\n << Add message to explain Tools here >> \n\n",
           'send': "How to Send Laisee\n\n << Add message to explain Send Options here >> \n\n",
           'settings': "<b> Settings </b> \n\n << add good settings message here>> \n\n\n",
           'topup': "<b> Top Up Options</b> \n\n << add good explanation message here>> \n\n\n",
           'username': 'Please set a username in telegram in order use this bot.',
           'welcome': 'Welcome to Lightning Laisee\n\n << add detailed welcome message here >> \n',
           'wallet':  "Your Wallet Balance\n",
           'laisee_amts': 'Tell us how much you want to send by selecting an option below.\nBe sure to have enough balance! Or, customize: `/laisee  < amount > `',
           'send_detail': "To send to another user, type in the message box:\n/send amt @username \n\nFor Example: /send 100 @user123"
           }


en_LNaddress_info = [ "With a Lightning Address you can send sats to this wallet from another service, such as @lntxbot or a lightning enabled wallet. \n\n\n ",
                    "Top Up Example: /send 1000 username@laisee.org \n\n\n", 
                    "This Lightning Address is currently set to accept between <b> 10 to 10,000 sats maximum in a transaction. </b>\n\n",
                    "If you just created your wallet, please wait a few minutes for the address to deploy. ",
                    "If you are having trouble accessing the Lightning address, please visit the helpdesk."]



en_send_created = "Congrats! Laisee has been sent to Telegram user."
en_laisee_created =  "Congrats! here is your Laisee image. You can now forward this to anyone you like. \n\nRemember to top up your wallet! \n<< fill in more details here>> \n"


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
