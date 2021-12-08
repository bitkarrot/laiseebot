import asyncio
from aiohttp.client import ClientSession
from supabase import Client

import datetime
import os
import subprocess
import json

from pylnbits.config import Config
from pylnbits.user_manager import UserManager
from pylnbits.user_wallet import UserWallet
from pylnbits.lnurl_p import LnurlPay
from local_config import LConfig

import pyqrcode
from jinja2 import Template 
import subprocess
import base64


# test user creation with pylnbits and supabase-py
# laisee user = supabase + lnbits accounts

# here we assume git repo already cloned and in current working dir
# rewrite subprocess commits with simplegit in node.js, 
# python-git not suitable for long running processes
git_repo_path = "../laisee-frontpage/public/.well-known/lnurlp/"



def create_laisee_qrcode(lnurl: str, idnumber: str, expires: str, sats: str, template_file: str):
    '''
    EDIT YOUR TEMPLATE FILE to refer to lnurl_file and qr_code, idnumber, expires and sats with {{ }}
    example: {{sats}}
    '''
    try:
        lnurl_file = "images/lnurl_" + idnumber + ".png" # make this id number based to prevent collision
        output_svg = 'images/output_' + idnumber + '.svg'
        output_png = 'images/output_' + idnumber + '.png'

        # todo: check if lnurl is valid
        pyqr = pyqrcode.create(lnurl,  error='H')

        # change your QR code foreground and background colors here
        pyqr.png(lnurl_file, scale=3, module_color=[170,0,0,255], background=[255, 255, 255])
    
        with open(lnurl_file, 'rb') as fp:
            data = fp.read()
            base64qr = base64.b64encode(data).decode('utf-8')
            # print(base64qr)
            fp.close()

        qr_code = "\"data:image/png;base64," + base64qr + "\""

        with open(template_file, 'r') as tf:
            templ = tf.read()
            tf.close()

        tm = Template(templ)
        msg = tm.render(qrcode=qr_code, idnumber=idnumber, expires=expires, sats=sats)

        with open(output_svg, 'w') as f:
            f.write(msg)
            f.close()
        subprocess.run(['rsvg-convert', output_svg, '-o', output_png, '-w' , '600'], cwd=".")
        return output_png
    except Exception as e: 
        return str(e)


def get_QRimg(telegram: str, bolt11: str):
    try:
        tip_file = '/tmp/deposit_' + telegram + '.png'
        print(f' tip file: { tip_file } ')
        qr = pyqrcode.create(bolt11) 
        qr.png(tip_file, scale=3, module_color=[0,0,0,128], background=[0xff, 0xff, 0xff])
        return tip_file
    except Exception as e:
        print(e)
        return { 
            "msg" : "Not a valid Lightning Address. Sorry!"
        }


async def activate_url(url: str, session):
    # async with ClientSession() as session:
    async with session.get(url) as response:
        if response.status == 200: 
            return True
        else: 
            return False


async def activate_extensions(url: str, user_id: str, session: ClientSession ): 
    # Post activate extension for user_id
    extension_list = ['lnurlp', 'withdraw','lndhub']
    tasks = []
    for i in extension_list:
        exturl = url + "/extensions?usr=" + user_id + "&enable="  + i
        print(f'enable extension: {exturl}')
        task = asyncio.ensure_future(activate_url(exturl, session))
        tasks.append(task)
    result = await asyncio.wait(tasks)
    print(result)
    if any(result):
        print(f"OK all extensions added {extension_list} , no problems")
        return True
    else: 
        print(" failed activate at least one extension, try again?")
        return False


async def create_new_lnbits(user_manager: UserManager, user_name: str, admin_id: str):
    # Post Create User + Initial
    wallet_name = user_name
    print(f"admin_id: {admin_id}, username: {user_name}, walletname: {wallet_name}")
    created_status = await user_manager.post_user_initial(admin_id, user_name, wallet_name)
    print(f"User + Initial: created wallet: {created_status}\n")
    return created_status


async def check_supauser_exists(supabase: Client, telegram_name: str):
    user = supabase.table('profiles').select('*').eq('username', telegram_name).execute()
    if len(user['data']) == 0:
        return False
    else: 
        return user


async def create_supauser(supabase: Client, lnbits_data: dict, uuid: str):
    wallet_data = lnbits_data['wallets'][0]
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z")  
    # insert an entry into profiles table
    new_user = {'id': uuid,
                'username': lnbits_data['name'],  # must be unique
                'lnbits_user_id': lnbits_data['id'],
                'admin_key': wallet_data['adminkey'],
                'invoice_key': wallet_data['inkey'],
                'wallet_id': wallet_data['id'],
                'lnaddress': lnbits_data['name'] + "@laisee.org", # must be unique
                'website': '', 
                'avatar_url': '', 
                'updated_at': now}
    # check if insert successful
    data = supabase.table('profiles').insert(new_user).execute()
    return data


async def get_supauser_data(supabase: Client, username: str): 
    data = supabase.table('profiles').select('*').eq('username', username).execute()
    # print(f"select result: { data }")
    return data



async def create_lnaddress(session: ClientSession, wallet_config: LConfig):
    try:
        # first check to see if the address exists or not
        telegram_name = wallet_config.telegram
        # simple check: look at github repo for telegram named file in folder  
        # doesn't guarantee validity, if not deleted from previous account creation 
        # assume git repo in 1 level up
        git_entry = "../laisee-frontpage/public/.well-known/" + telegram_name
        if os.path.exists(git_entry):
            return True
        # create ln address w/laisee_email
        laisee_email = telegram_name + "@laisee.org"
        # create lnurlp link, add to github in file called 'telegram_name'
        lnurlp = LnurlPay(wallet_config, session)
        # create pay link
        body = {"description": "LN address for " + laisee_email,
                "amount": 10,
                "max": 10000,
                "min": 10,
                "comment_chars": 100}

        newlink = await lnurlp.create_paylink(body=body)
        pay_id = newlink['id']
        print(f'lightning address: {laisee_email}')
        print(f"create pay link with body: {body}, result link: {newlink}, payid: {pay_id} \n")

        # TODO Check that the paylink is actually valid 
        callback = wallet_config.lnbits_url + "/lnurlp/api/v1/lnurl/cb/" + str(pay_id)
        print(callback)
        metadata = "Pay to " + laisee_email
        ln_data = {
            "callback": callback, 
            "maxSendable": body['max']*1000, 
            "metadata": "[[\"text/plain\", \"" + metadata + "\"]]", 
            "minSendable": body['min']*1000, 
            "tag": "payRequest"
        }

        new_path = git_repo_path + telegram_name
        # pull down for fresh updates before making edits to repo
        subprocess.run(['git', 'pull'], cwd=git_repo_path)
        
        # check to make sure file doesn't exist. if its does, then remove and create new
        if os.path.isfile(new_path):
            os.remove(new_path)
        with open (new_path, 'w') as fp:
            fp.write(json.dumps(ln_data))

        if os.path.isfile(new_path):
            # TODO asynchronous subprocess, handle exceptions if git cannot be reached.
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z")  
            subprocess.run(['git', 'add', telegram_name ], cwd=git_repo_path)
            subprocess.run(['git', 'commit', '-m', "Add " + telegram_name + " added: " + now], cwd=git_repo_path)
            subprocess.run(['git', 'push'], cwd=git_repo_path)
            return True

    except Exception as e: 
        print("Error creating lightning address: " + str(e))
        return False

    # remember the Lightning Address is not instantaneously available, usually within 5 min
    # it relies on a rebuild and deploy to vercel of the git repo after successfully pushed. 


async def delete_lnaddress(session: ClientSession, wallet_config: LConfig):
    try:
        # get pay id from github entry
        telegram_name = wallet_config.telegram
        new_path = git_repo_path + telegram_name
        print(f'Lightning Address File to delete : {new_path}')

        with open(new_path, 'r') as f:
            json_content = f.read()
            print(f'file content: {json_content}, type: {type(json_content)}')
            datablock = json.loads(json_content)
            lnbits_paylink = datablock["callback"]
            print(f'lnbits paylink: {lnbits_paylink}')
            pay_id = lnbits_paylink.split('/').pop()
            print(f'pay id: {pay_id}')
            # delete lnurlp if any
            lnurlp = LnurlPay(wallet_config, session)
            delete_result = await lnurlp.delete_paylink(pay_id)
            print(f'delete paylink result: {delete_result} ')

        # TODO: node updategit.cjs -d <filename> >> ./logfile 2>&1`
        subprocess.run(['git', 'pull'], cwd=git_repo_path)
        # check for LN file. if it exists, then remove 
        if os.path.isfile(new_path):
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z")
            subprocess.run(['git', 'rm', telegram_name], cwd=git_repo_path)
            subprocess.run(['git', 'commit', '-m', "Delete " + telegram_name + ": " + now], cwd=git_repo_path)
            subprocess.run(['git', 'push'], cwd=git_repo_path)
            return True
    
    except Exception as e: 
        print("Error deleting lightning address: " + str(e))
        return False



async def create_laisee_user(telegram_name: str, config, session: ClientSession, supabase: Client): 
    um = UserManager(config, session)
    lnbits_url = config.lnbits_url
    adminkey = config.admin_key

    laisee_email: str = telegram_name + "@laisee.org"
    passkey: str = os.environ.get("PASSKEY")
    random_password = passkey
    user = supabase.auth.sign_up(email=laisee_email, password=random_password, phone=None)
    print(f'Sign up new user: {user} \n')
    # check for timeout error here or failure to create, then skip rest b/c no uuid

    # create new lnbits user
    uuid = user['user']['id']
    create_result = await create_new_lnbits(um, telegram_name, adminkey)
    user_id = create_result['id']
    # check for timeout error
    
    # create supabase user entry with lnbits data
    supabase_data = await create_supauser(supabase, create_result, uuid)
    print(f'supabase_results: {supabase_data}')
    if supabase_data.get("status_code") in (200, 201):
        print(f'supabase_insert success')

    # activate LNbits extensions
    result = await activate_extensions(lnbits_url, user_id, session)
    print(f'activate extensions result: {result}')
    lnbits_link = lnbits_url + "/wallet?usr=" + user_id
    print(lnbits_link)

    # make wallet manager
    wallet_data = create_result['wallets'][0]
    wallet_config = LConfig(in_key= wallet_data['inkey'], 
                            admin_key= wallet_data['adminkey'], 
                            lnbits_url=lnbits_url, 
                            user_id=create_result['id'],
                            wallet_id=wallet_data['id'],
                            telegram=telegram_name,
                            lnaddress=laisee_email,
                            uuid=user['user']['id'])

    # create UserWallet object
    user_wallet = UserWallet(config=wallet_config, session=session) 

    return user_wallet


async def get_laisee_user(telegram_name: str, supabase: Client, lnbits_url: str):
    user_data = await get_supauser_data(supabase, telegram_name)
    # print(f'Supabase user data : {user_data} ') 
    user_invoicekey = user_data['data'][0]['invoice_key']
    user_adminkey = user_data['data'][0]['admin_key']
    user_id = user_data['data'][0]['lnbits_user_id'] 
    wallet_id = user_data['data'][0]['wallet_id']
    lnaddress = user_data['data'][0]['lnaddress']
    uuid = user_data['data'][0]['id']
    # check above values are non-null before preceeding

    # local config for tg users, with supabase details, and lnbits userid
    wallet_config = LConfig(in_key=user_invoicekey, 
                            admin_key=user_adminkey, 
                            lnbits_url=lnbits_url, 
                            user_id=user_id,
                            wallet_id=wallet_id,
                            lnaddress=lnaddress,
                            telegram=telegram_name,
                            uuid=uuid)
    
    return wallet_config
 

async def delete_laisee_user(wallet_config: LConfig, master_config: Config, supabase: Client):
    # deletes both lnbits and supabase accounts 
    # (separate into 2 methods, catch errors)
    inkey = master_config.in_key
    lnbits_url = master_config.lnbits_url
    # delete lnbits
    user_id = wallet_config.user_id
    uuid = wallet_config.uuid
    telegram_name = wallet_config.telegram
    delete_call = "curl -X DELETE " + lnbits_url + "/usermanager/api/v1/users/" + user_id + " -H \"X-Api-Key: " + inkey + "\""
    result = os.system(delete_call)
    print(f'LNBits delete result: {result}')

    # delete supbase profile 
    data = supabase.table('profiles').delete().eq('username', telegram_name).execute()
    print(f"delete profile result: {data}")

    # delete supbase auth 
    # supabase python library does not have auth methods yet, 
    # temporarily use the js library
    from subprocess import Popen, PIPE
    sensor = Popen(['node', 'delete_supauser.js', uuid], stdout=PIPE)
    out = sensor.stdout.read() 
    res = out.decode('utf-8').rstrip()
    print(f"delete supabase auth user: {res}")
    return data, res



async def update_supauser_email(wallet_config: LConfig, supabase: Client):
    # web-todo: this is the supabase auth email, how to pull email from uuid?
    # should we keep record of true email in the wallet-config?
    return "supabase email address updated"

