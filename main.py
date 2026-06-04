import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging to view inside the Render dashboard logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fallback token checking
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"Hi {user.first_name}! 👋 Welcome to **ChronoTask Utility Bot**.\n\n"
        "I am running 24/7 as a background worker with zero external API dependencies.\n\n"
        "**Available Commands:**\n"
        "🕒 `/time` - Get detailed current date & time variations.\n"
        "⏳ `/timer <seconds>` - Set an isolated focus timer.\n"
        "🔤 `/caps <text>` - Convert any text to capital letters.\n"
        "📊 `/stats` - Check system metric strings.\n\n"
        "Or just type any text message and I will echo its diagnostic character length!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the current server UTC time elements."""
    now = datetime.utcnow()
    time_response = (
        "📊 **Current Server Metrics (UTC):**\n"
        f"• Date: `{now.strftime('%Y-%m-%d')}`\n"
        f"• Time (24h): `{now.strftime('%H:%M:%S')}`\n"
        f"• Day of Week: `{now.strftime('%A')}`\n"
        f"• Day of Year: `{now.strftime('%j')}/365`"
    )
    await update.message.reply_text(time_response, parse_mode="Markdown")

async def caps_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Converts user text to uppercase arguments."""
    if not context.args:
        await update.message.reply_text("Please provide text! Example: `/caps hello world`", parse_mode="Markdown")
        return
    text_to_caps = " ".join(context.args).upper()
    await update.message.reply_text(f"🔤 **Uppercase Output:**\n`{text_to_caps}`", parse_mode="Markdown")

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback function that sends the timer alert."""
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id, 
        text=f"⏰ **Timer finished!** Your requested `{job.data}` second interval is up.",
        parse_mode="Markdown"
    )

async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Adds a background Job to the built-in JobQueue."""
    chat_id = update.effective_message.chat_id
    try:
        # Extract the duration from the message arguments
        due = float(context.args[0])
        if due <= 0:
            await update.message.reply_text("Please specify a positive number of seconds.")
            return

        # Use the built-in job_queue provided natively by python-telegram-bot
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=int(due))
        await update.message.reply_text(f"⏳ Timer successfully set for `{int(due)}` seconds!", parse_mode="Markdown")

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/timer <seconds>` (e.g., `/timer 60`)", parse_mode="Markdown")

async def echo_diagnostics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echos back text diagnostics metrics."""
    user_text = update.message.text
    char_count = len(user_text)
    word_count = len(user_text.split())
    
    response = (
        "📝 **Text Diagnostic Tool**\n"
        f"• Your Text: \"{user_text}\"\n"
        f"• Characters: `{char_count}`\n"
        f"• Words: `{word_count}`"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

def main() -> None:
    """Start the bot using long polling."""
    if not TOKEN:
        logger.critical("Error: TELEGRAM_BOT_TOKEN environment variable is missing!")
        return

    # Build the application container natively
    application = Application.builder().token(TOKEN).build()

    # Register text commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("caps", caps_command))
    application.add_handler(CommandHandler("timer", timer_command))

    # Register default messaging diagnostics fallback
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_diagnostics))

    # Run polling loop indefinitely (Perfect environment setup for Background Worker types)
    logger.info("Bot starting with Long Polling via Render Background Worker...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
