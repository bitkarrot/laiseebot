# laiseebot
Telegram Bot for LN Laisees

# commands list
- **/help** - get help commands, and a welcome message on how to use the bot
- **/start** - automatically creates a wallet on LNBITS with LNURLp extension. 
> * Automatically creates a lnaddress with format of username@laisee.org, based on the telegram username. 

## LaiseeBot Functions
- **/rates** - what daily exchange rate is between sats to hkd and usd

## transactions
- **/laisee** - /laisee <amt> username, Sends a laisee to another, has sub menu pick image/msg. 
   cannot send to user if they don't have a telegram account,
   notify user their recipient needs to start a conversation in order to receive their gift.    
- **/send** - /send <amt> telegram username
- **/invoice** - /invoice <amt> , generate lightning invoice
   
## wallet functionality on lnbits
- **/balance** - get current wallet balance on lnbits
- Top Up Wallet
   
## create LN address [ on start ]
   [WARNING: if end user modifies metadata on lnbits or changes TG name, the LN address needs to be updated on github, these two are connected. ]

## lnurlP extension on lnbits
- see fill command above, metadata for LN address that must be synced between lnbits and github are below:
    * amount: 100- 100000 sat
    * on success: display message 
    * dispatches webhook to : <<>>

## lndhub extension
- **/lndhub** or **/bluewallet** - get LNDHUB invoice url or admin url [admin, invoice sub command] that can be used w/external wallet
- **/withdraw** - get LNURL Withdraw QR code to drain wallet

========

## WIP LIST

1) [Infrastructure] pylnbits module - clean up unit tests.
    * https://github.com/lightningames/pylnbits.git

2) [Infrastructure] Supabase -  
    * Write a Module - db access for records, use curl methods as current library is incomplete
    * Data: 
      - TG Username
      - LN Address (username@domain.com)
      - LNBits url
      - invoice_key (lnbits, needed for send/receive/lookup functions)
      - admin_key (lnbits, needed to enable extensions and create lnurlp, used with LN Addresses) 
      - Email Address (tied to auth on supabase, accessible via web interface)
      - optional avatar (web interface, for future implementation)
      - optional website. (web interface)  

3) [FrontEnd] Telegram: Stitch above together with Telegram bot menu and methods

4) [Infrastructure] LN Addresses:
    * LN Address entries by updating git repo: github.com/bitkarrot/laisee-frontpage
    * deployed site has .well-known enabled
 
5) [FrontEnd] Web framework: https://laisee-test.vercel.app/
    * can be easily extended in future to embed lnbits functions
    * supabase backend
