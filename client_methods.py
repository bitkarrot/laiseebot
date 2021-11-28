import asyncio

from aiohttp.client import ClientSession
from local_config import LConfig
from supabase import create_client, Client
import os

from pylnbits.config import Config
from pylnbits.user_wallet import UserWallet

from laisee_utils import get_laisee_user, create_laisee_user, delete_laisee_user
from laisee_utils import check_supauser_exists, create_lnaddress, delete_lnaddress, get_lnbits_link


async def delete_user(wallet_config: LConfig, masterc: Config, supabase: Client, session: ClientSession):
    # master config required for LNBits deletion
    print(f'==============DELETE LIGHTNING ADDRESS==================')
    lnresult = await delete_lnaddress(session, wallet_config)
    print(f'lightning address deleted: { lnresult }')

    # delete user from lnbits, supabase
    print(f'==== DELETE LAISEE USER from LNbits and Supabase ====')
    data,res =  await delete_laisee_user(wallet_config, masterc, supabase)
    print(f'delete user result: data: {data}, \n delete res: {res}')
    suparesult = False
    if data['status_code'] == 200:
        suparesult = True
    lnbitsresult  = bool(res)
    result = [lnresult, suparesult, lnbitsresult]
    # parse data, res lnresult, and return 1 unified result
    return result
        

async def create_user(telegram_name: str, masterc: Config, supabase: Client, session: ClientSession):
    # if user exists, don't create new user
    user = await check_supauser_exists(supabase, telegram_name)
    # check supabase DB for user, if none, then create new
    if user:
        print(f'==== CREATE LAISEE USER from LNbits and Supabase ====')
        wallet_config = await get_laisee_user(telegram_name, supabase, masterc.lnbits_url)
        user_wallet = UserWallet(config=wallet_config, session=session)
    else:
        print(f'==== FETCTHING LAISEE USER from LNbits and Supabase ====')
        user_wallet = await create_laisee_user(telegram_name, masterc, session, supabase)

    wallet_config = user_wallet.config
    print(wallet_config.lnbits_url)

    print(f'==============CREATE LIGHTNING ADDRESS==================')
    # create lightning address - done, addresses pushes to web in about 5 min
    # if it does not, check github repo if there was an error
    lnresult = await create_lnaddress(session, wallet_config)
    print(f"Lightning Address creation result: { lnresult }")
    
    return wallet_config
    
 
async def get_balance(user_wallet: UserWallet):
    # get wallet details (todo parse)
    walletinfo = await user_wallet.get_wallet_details()
    balance = walletinfo['balance']
    # print(f"user wallet info : {walletinfo}")
    print(f'Your Wallet Balance: {balance} sats')
    return balance


'''

async def main():
    async with ClientSession() as session:

        masterc = Config(config_file="config.yml")
        supa_url: str = os.environ.get("SUPABASE_URL")
        supa_key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(supa_url, supa_key)

        telegram_name = 'hellon00b'

        wallet_config = await create_user(telegram_name, masterc, supabase, session)

        user_wallet = UserWallet(config=wallet_config, session=session)
        balance = await get_balance(user_wallet)
        print(f'balance from wallet: {balance}')  

        lnbits_link = await get_lnbits_link(wallet_config)
        print(f'Lnbits Link: {lnbits_link}')

        del_result = await delete_user(wallet_config, masterc, supabase, session)
        print(f'Deletion result: {del_result}')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

'''