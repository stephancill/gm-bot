#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import config
import datetime
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def handle_message(update: Update, context: CallbackContext) -> None:
    """Saves the user message."""
    # Check if message contains gm
    message = "".join([x for x in update.message.text if x.isalpha()])
    if message.strip().lower() == "gm":
        # 1. Forward a gm message
        # 2. Forward this message to channel
        # 3. Store message and chat id
        chat_id = update.message.chat_id

        last_gm = context.user_data.get("last_gm")
        time_now = datetime.datetime.utcnow()
        if last_gm:
            delta: datetime.timedelta = time_now - last_gm
            if delta < datetime.timedelta(hours=12):
                update.message.reply_text("Yeah yeah gm")
                return

        context.user_data["last_gm"] = time_now

        last_from_chat_id = context.bot_data.get("last_from_chat_id")
        last_message_id = context.bot_data.get("last_message_id")

        if last_from_chat_id and last_message_id:
            context.bot.forward_message(chat_id, last_from_chat_id, last_message_id)
        else:
            update.message.reply_text("gm! 💫")
        
        this_chat_id = update.message.chat_id
        this_message_id = update.message.message_id

        context.bot_data["last_from_chat_id"] = this_chat_id
        context.bot_data["last_message_id"] = this_message_id
        
        context.bot.forward_message(config.CHANNEL_ID, this_chat_id, this_message_id)
    else:
        update.message.reply_text("That isn't a gm message 🤔")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(config.PERSISTENCE_PATH)
    updater = Updater(config.BOT_TOKEN, persistence=persistence, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command & ~Filters.chat_type.channel, handle_message))

    # Start the Bot
    if config.DEBUG:
        updater.start_polling()
    else:
        updater.bot.delete_webhook()
        updater.start_webhook(listen="0.0.0.0",
                        port=config.PORT,
                        url_path=config.BOT_TOKEN,
                        webhook_url=f"{config.APP_URL}/{config.BOT_TOKEN}")

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()