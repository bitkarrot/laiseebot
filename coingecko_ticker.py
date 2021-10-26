from pycoingecko import CoinGeckoAPI
from constants import currencylist
import time

def get_btcrates():
    currencies = list(currencylist.keys())
    cg = CoinGeckoAPI()
    price = cg.get_price(ids='bitcoin', vs_currencies=currencies, include_last_updated_at='true')
    last_update = price['bitcoin']['last_updated_at']
    readable_time = time.ctime(last_update)
    rateinfo = f'<b>Coingecko</b>, Last Updated:\n{readable_time}\n\n'
    for symbol in currencies:
        fiat = "{:,}".format(price['bitcoin'][symbol])
        rateinfo += f'<b>BTC/{symbol.upper()}</b>\t\t\t{currencylist[symbol].strip()}{fiat}\n'
    return rateinfo

    
def get_supported_currencies():
    cg = CoinGeckoAPI()
    currencies = cg.get_supported_vs_currencies()
    #print(currencies)
    return currencies

# /sats <amount> <fiat> e.g. /sats 100 USD
# 100,000,000 sats = 1 btc
def sats(amount, symbol, command):
    satsperbtc = 100000000
    sym = symbol.lower()
    msg = ''
    if '@' in command:
        command = command.split('@')[0]
    print(command)
    
    currencies = get_supported_currencies()
    if sym not in currencies:
        msg = 'Fiat currency not found. Try another?'
        return msg
    
    cg = CoinGeckoAPI()
    price = cg.get_price(ids='bitcoin', vs_currencies=symbol)
    rate = price['bitcoin'][sym]

    if command == '/btc':
        fiat = rate* (amount)
        fiat_amt = "%.2f" % fiat
        msg = f'{fiat_amt} {symbol.upper()}'
    if command == '/sats':
        fiat = rate* (amount/satsperbtc)
        fiat_amt = "%.2f" % fiat
        msg = f'{fiat_amt} {symbol.upper()}'
    elif command == '/fiat':
        btc = amount/rate
        btc_amt = "%.8f" % btc
        sats = int(satsperbtc * btc)
        msg = f'{btc_amt} BTC or {sats} sats' 
    return msg

    
def sats_convert(rawtext):
    try:
        if rawtext is None:
            return 'Please give an amount and a symbol, e.g. 1000 usd'
        
        content = rawtext.split(' ')
        print(content)
        
        amt = float(content[1].strip())
        fiatsym = content[2].strip()
        command = content[0]
        msg = sats(amt, fiatsym, command)
        return msg
    except Exception as e:
        print(e)
        content = 'Cannot parse parameters, Error\n\n'
        content += 'Usage:\n/btc 0.04 USD \t[btc to fiat]\n'
        content += '/sats 1000 HKD \t[sats to fiat]\n'
        content += '/fiat 100 HKD \t[fiat to btc/sats]\n'
        return content



if __name__ == '__main__':
    
    # real simple 'unit' test
    command = '/sats 100 USD'
    print(command)
    msg = sats_convert(command)
    print(msg + "\n")

    command = '/btc 0.1337 USD'
    print(command)
    msg = sats_convert(command)
    print(msg + "\n")
    
    command = '/fiat 1 USD'
    print(command)
    msg = sats_convert(command)
    print(msg + "\n")
    
    command = '/fiat asdfa USD'
    print(command)
    msg = sats_convert(command)
    print(msg + "\n")
