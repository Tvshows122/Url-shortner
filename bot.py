import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import os

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for user API keys
user_api_keys = {}

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Use /setapikey <your_api_key> to set your API key. Then send a URL to shorten it.')

def setapikey(update: Update, context: CallbackContext) -> None:
    """Set the user's API key."""
    if len(context.args) != 1:
        update.message.reply_text('Usage: /setapikey <your_api_key>')
        return

    user_id = update.message.from_user.id
    api_key = context.args[0]
    user_api_keys[user_id] = api_key
    update.message.reply_text('Your API key has been set!')

def shorten_url(update: Update, context: CallbackContext) -> None:
    """Shorten the URL provided by the user."""
    user_id = update.message.from_user.id
    if user_id not in user_api_keys:
        update.message.reply_text('You need to set your API key first using /setapikey <your_api_key>')
        return

    long_url = update.message.text
    api_key = user_api_keys[user_id]

    # BM Links URL shortener API endpoint
    URL_SHORTENER_API_ENDPOINT = 'https://bmlinks.com/api'

    # Call BM Links URL shortener API
    response = requests.get(URL_SHORTENER_API_ENDPOINT, params={
        'api': api_key,
        'url': long_url,
        'format': 'json'
    })

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            short_url = data.get('shortenedUrl')
            update.message.reply_text(f'Short URL: {short_url}')
        else:
            update.message.reply_text('Failed to shorten the URL. Please check your API key and the URL.')
    else:
        update.message.reply_text('Failed to shorten the URL. Please try again.')

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    # On different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("setapikey", setapikey))

    # On non-command text messages, try to shorten the URL
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, shorten_url))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
      
