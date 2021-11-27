from yaml import safe_load
from pylnbits.config import Config
# import os

# LConfig extends pylnbits config with supabase, lnaddress and other lnbits parameters

class LConfig(Config):
    def __init__(self, config_file: str = None, 
                        in_key: str = None, 
                        admin_key: str = None, 
                        lnbits_url: str = None, 
                        user_id: str = None,
                        wallet_id: str = None, 
                        lnaddress: str = None,
                        telegram: str = None,
                        uuid: str = None):

        self._in_key = in_key
        self._lnbits_url = lnbits_url
        self._admin_key = admin_key

        self._user_id = user_id
        self._wallet_id = wallet_id
        self._lnaddress = lnaddress
        self._telegram = telegram
        self._uuid = uuid # supabase uuid


        try:
            if config_file:
                with open(config_file, "rb") as f:
                    cfile = safe_load(f)
                    # print(cfile)
                f.close()
                self._in_key = cfile["in_key"]
                self._lnbits_url = cfile["lnbits_url"]
                self._admin_key = cfile["admin_key"]
        except Exception as e:
            print(e)
            return e


    @property
    def uuid(self):
        return self._uuid

    @property
    def telegram(self):
        return self._telegram

    @property
    def lnaddress(self):
        return self._lnaddress

    @property
    def user_id(self):
        return self._user_id

    @property
    def wallet_id(self):
        return self._wallet_id



if __name__ == "__main__":
    c = LConfig(config_file="./config.yml")

    print(c.in_key)
    print(c.lnbits_url)
    print(c.admin_key)
    print(c.headers())
    print(c.invoice_headers())
    print(c.admin_headers())
