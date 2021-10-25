const { Telegraf, Markup } = require('telegraf')
require('dotenv').config();

const token = process.env.BOT_TOKEN
if (token === undefined) {
    throw new Error('BOT_TOKEN must be provided!')
}
const CoinGecko = require('coingecko-api');
const CoinGeckoClient = new CoinGecko();

const bot = new Telegraf(token)
    //bot.use(Telegraf.log())

let startMessage = "Welcome to the Laisee Bot"
let helpMessage = "This is the help message"
let reply = 'fetching update!'

bot.start((ctx) =>
    ctx.reply(startMessage, Markup
        .keyboard([
            ['/help', '/list'],
            ['/info', '/update']
        ])
        .oneTime()
        .resize()
    )
)

bot.help((ctx) => ctx.reply(helpMessage))

bot.command('pyramid', (ctx) => {
    return ctx.reply(
        'Keyboard wrap',
        Markup.keyboard(['one', 'two', 'three', 'four'], {
            wrap: (btn, index, currentRow) => currentRow.length >= (index + 1) / 2
        })
    )
})

bot.command('update', (ctx) => ctx.reply(reply))

bot.command('info', (ctx) => {
    ctx.reply(helpMessage)
    let reply = 'Data from Coingecko. http://coingecko.com'
    ctx.reply(reply)
})

bot.command('list', (ctx) => {
    let p = " foo bar baz"
    ctx.replyWithMarkdown('*My List*\n\n' + p)
})

bot.on('sticker', (ctx) => ctx.reply('👍'))

bot.on('inline_query', (ctx) => {
    const result = [1, 2, 3, 4, 5]
        // Explicit usage
    ctx.telegram.answerInlineQuery(ctx.inlineQuery.id, result)
        // Using context shortcut
    ctx.answerInlineQuery(result)
})

// bot start
bot.launch()
console.log("Launching Laisee LN Bot..... ")

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))