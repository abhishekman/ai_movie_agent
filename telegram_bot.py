from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import TELEGRAM_BOT_TOKEN

from agent import run_agent

from database.db import (
    create_tables,
    create_user,
    get_user
)


# Create database tables
create_tables()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = str(update.effective_chat.id)

    name = update.effective_user.first_name or "Telegram User"

    # Create Telegram user if not already exists
    create_user(name, chat_id)

    await update.message.reply_text(
        "🎬 Hello! I'm your AI Movie Agent.\n\n"
        "Ask me for movie recommendations!"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_message = update.message.text

    # Telegram user's unique ID
    chat_id = str(update.effective_chat.id)

    name = update.effective_user.first_name or "Telegram User"

    print("User:", user_message)
    print("Chat ID:", chat_id)

    # Create user if not already exists
    create_user(name, chat_id)

    # Get user from database
    user = get_user(chat_id)

    if not user:
        await update.message.reply_text(
            "Sorry, I couldn't find your user account."
        )
        return

    # Database user ID
    user_id = user[0]

    # Run AI Movie Agent
    response = run_agent(
        user_id,
        user_message
    )

    # Send AI response to Telegram
    await update.message.reply_text(response)


def main():

    app = Application.builder().token(
        TELEGRAM_BOT_TOKEN
    ).build()

    # /start command
    app.add_handler(
        CommandHandler("start", start)
    )

    # Normal text messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🤖 Telegram AI Movie Agent is running...")

    app.run_polling()


if __name__ == "__main__":
    main()