import asyncio
from aiohttp.client import ClientSession
from supabase import create_client, Client
import os

from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet

from laisee_utils import get_laisee_user, create_laisee_user, delete_laisee_user
from laisee_utils import check_supauser_exists, create_lnaddress, delete_lnaddress, get_lnbits_link

# check transactions. (receiving, there are no websockets, cron pull?)

async def main():
    # setup application 
    # master key for creating accounts
    # run node update_git.cjs -p to pull down laisee-frontpage repo 
    # git clone https://github.com/bitkarrot/laisee-frontpage.git
    
    masterc = Config(config_file="config.yml")
    lnbits_url = masterc.lnbits_url
    supa_url: str = os.environ.get("SUPABASE_URL")
    supa_key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(supa_url, supa_key)

    async with ClientSession() as session:

        telegram_name = 'hellon00b'

        # if user exists, don't create new user
        user = await check_supauser_exists(supabase, telegram_name)
        # check supabase DB for user, if none, then create new
        if user:
            wallet_config = await get_laisee_user(telegram_name, supabase, lnbits_url)
            user_wallet = UserWallet(config=wallet_config, session=session)
        else:
            user_wallet = await create_laisee_user(telegram_name, masterc, session, supabase)

        wallet_config = user_wallet.config
        print(wallet_config.lnbits_url)

        # get wallet details (todo parse)
        walletinfo = await user_wallet.get_wallet_details()
        balance = walletinfo['balance']
        # print(f"user wallet info : {walletinfo}")
        print(f'Your Wallet Balance: {balance} sats')

        # get lnbits link
        lnbits_link = await get_lnbits_link(wallet_config)
        print(f'Lnbits Link: {lnbits_link}')

        # create lightning address - done, addresses pushes to web in about 5 min
        # if it does not, check github repo if there was an error
        print(f'==== CREATE LN ADDRESS ==== ')
        lnresult = await create_lnaddress(session, wallet_config)
        print(f"Lightning Address creation result: { lnresult }")
    
        # delete lightning address
        print(f'==== DELETE LN ADDRESS ==== ')
        lnresult = await delete_lnaddress(session, wallet_config)
        print(f'lightning address deleted: { lnresult }')

        # delete user from lnbits, supabase
        data,res =  await delete_laisee_user(wallet_config, masterc, supabase)
        print(f'delete user result: data: {data}, \n delete res: {res}')



loop = asyncio.get_event_loop()
loop.run_until_complete(main())

