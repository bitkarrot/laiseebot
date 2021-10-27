# laiseebot
Telegram Bot for LN Laisees

# commands list
- **/help** - get help commands, and a welcome message on how to use the bot
- **/start** - automatically creates a wallet on LNBITS with LNURLp extension. 
> * Automatically creates a lnaddress with format of username@laisee.org, based on the telegram username. 
> * LN address cannot be changed once in play. [ lnbits url, tg username data stored on supabase] -
> * Issue 1: Should let the LN address be an option later or should we have it as default?
> * Issue 2: If the user stops the bot, and restarts, it should not recreate, just do a db look up. 
> * Issue 3: How do we connect this with the front end where the user registers with their email? 
> Do we offer this as a paid service? e.g. XXX sats for a forwarder enabled. forwarders must be manually enabled on fastmail, requires human intervention. 


## LaiseeBot Functions
- **/image** - select an laisee image or upload your own to send and personalize 
- **/spin** - daily spins to win sats to your wallet, the more laisees you send, the higher chance to win sats from the giveaway pool 
- **/sats** - what daily exchange rate is between sats to hkd and usd

## transactions
- **/laisee** - /laisee <amt> username, Sends a laisee to another, has sub menu pick image/msg. 
   cannot send to user if they don't have a telegram account,
   notify user their recipient needs to start a conversation in order to receive their gift. 
   
- **/send** - /send <amt> username or LN address, just sends regular sats as normal
- **/receive** - /receive <amt> or <any amt> , shows QR code for receiving sats
   

## create LN address [ on start ]
- **/lnaddress** - view your ln address, email submenu option to add an email forwarder [WARNING: if end user modifies metadata on lnbits, the LN address needs to be updated on github, these two are connected. ]

## lndhub extension
- **/lndhub** or **/bluewallet** - get LNDHUB invoice url or admin url [admin, invoice sub command] that can be used w/external wallet

## wallet functionality on lnbits
- **/balance** - get current wallet balance on lnbits
- **/withdraw** - get LNURL Withdraw QR code to drain wallet
- **/lnbits** - get lnbits url so user can access interface directly

## exit functionality - main wallet on lnbits
- **/delete** - deletes LNBITS wallet, address and stops the bot, adds warning of any sats that are left in wallet will be donated/deleted.

## lnurlP extension on lnbits
- see fill command above, metadata for LN address that must be synced between lnbits and github are below:
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
    * Data to Store: 
      - TG Username
      - LN Address (username@domain.com)
      - LNBits url (e.g. https://bits.bitcoin.org.hk/lnurlp/?usr=XXXXXXX)
      - invoice_key (lnbits, needed for send/receive/lookup functions)
      - admin_key (lnbits, needed to enable extensions and create lnurlp, used with LN Addresses) 
      - Email Address (tied to auth on supabase, accessible via web interface)
      - optional avatar (web interface)
      - optional website. (web interface) 

   [ These last two columns were part of the demo from supabase so inherited properties, can remove anytime, esp if avatar images run out of space on data bucket.]  

3) [FrontEnd] Telegram: Stitch above together with Telegram bot menu and methods

4) [Infrastructure] LN Addresses: GitPython module
    * to add LN Address entries to website by updating git repo. 
    * current website has .well-known enabled
 
5) [FrontEnd] Web framerwork: https://laisee-test.vercel.app/
    * can be easily extended in future to embed lnbits functions
    * demo site has email magic link and simple profile setup: telegram username, email, avatar, website
    * data on supabase
