import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния
NAME, CURRENCY = range(2)

# URL для получения курсов валют
EXCHANGE_RATE_API = 'https://api.exchangerate-api.com/v4/latest/USD'


def get_exchange_rates():
    response = requests.get(EXCHANGE_RATE_API)
    data = response.json()
    rates = {
        'доллар': data['rates']['RUB'],
    }
    return rates


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Добрый день! Как вас зовут?")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text
    context.user_data['name'] = user_name

    rates = get_exchange_rates()
    response_message = (
        f"Рад знакомству, {user_name}! "
        f"Курс доллара: {rates['доллар']}, "
    )

    reply_markup = ReplyKeyboardMarkup([['Начать заново']], one_time_keyboard=True)
    await update.message.reply_text(response_message, reply_markup=reply_markup)

    return CURRENCY


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await start(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('До свидания!')
    return ConversationHandler.END


def main():
    TOKEN = '7929361567:AAESMzUJ0h3mmfFIgii5lU9TTPL4qYMOCxs'

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, restart)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()