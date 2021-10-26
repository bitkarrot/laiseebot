# laiseebot
Telegram Bot for LN Laisees

# commands list
- **/help** - get help commands, and a welcome message on how to use the bot
- **/start** - automatically creates a wallet on LNBITS with LNURLp extension. automatically creates a lnaddress with format of username@laisee.org, based on the telegram username. LN address cannot be changed once in play. [ lnbits url, tg username data stored on supabase] - i don't know if this is too much of if we should let the LN address be an option later. Also if the user stops the bot, and restarts, it should not recreate, just do a db look up. 

## Laisee Functions
- **/image** - select an laisee image or upload your own to send and personalize 
- **/spin** - daily spins to win sats to your wallet, the more laisees you send, the higher chance to win sats from the giveaway pool 
- **/sats** - what daily exchange rate is between sats to hkd and usd

## transactions
- **/laisee** - /laisee <amt> username, Sends a laisee to another, has sub menu pick image/msg. 
cannot send to user if they don't have a telegram account, notify user their recipient needs to start a conversation in order to receive their gift. 
- **/send** - /send <amt> username or LN address, just sends regular sats as normal
- **/receive** - /receive <amt> or <any amt> , shows QR code for receiving sats
- **/refill** - /refill <amt> to wallet via LN invoice, what if they only have BTC layer 1?

## create LN address [ on start ]
- **/lnaddress** - view your ln address, email submenu option to add an email forwarder

## lndhub extension
- **/lndhub** - get LNDHUB invoice url or admin url [admin, invoice sub command]

## wallet functionality on lnbits
- **/balance** - get current wallet balance on lnbits
- **/withdraw** - get LNURL Withdraw QR code to drain wallet
- **/export** - export wallet to Phone with QR Code
- **/rename** - rename wallet on lnbits
- **/lnbits** - get lnbits url so user can access interface directly

## exit functionality - main wallet on lnbits
- **/delete** - deletes LNBITS wallet, LN Email address and stops the bot, adds warning of any sats that are left in wallet will be donated. 

## lnurlP extension on lnbits
- see fill command above, sub commands to set are below:
    * amount: 100- 100000 sat
    * accepts commments
    * on success: display message 
    * dispatches webhook to : <<>>

========

## DEV TODO LIST

1) [Infrastructure] pylnbits module - clean up test cases and add missing methods to access lnbits
    * https://github.com/lightningames/pylnbits.git

2) [Infrastructure] Supabase -  
    * Write a Module - db access for records, use curl methods as current library is incomplete
    * Data to Store: Name, Username, LN Address, LNBits url, Email Address Forwarder (optional)

3) [FrontEnd] Telegram: Stitch above together with Telegram bot menu and methods

4) [Infrastructure] LN Addresses: GitPython module
    * to add LN Address entries to website by updating git repo. 
    * current website has .well-known enabled
 
5) [FrontEnd] Web framerwork: https://laisee-test.vercel.app/
    * can be easily extended in future to embed lnbits functions
    * demo site has email magic link and simple profile setup: name, email, avatar, website
    * data on supabase
