import os
import logging
import asyncio
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup explicit logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    user = update.effective_user
    welcome_text = (
        f"Hi {user.first_name}! 👋 Welcome to **ChronoTask Utility Bot**.\n\n"
        "I am running 24/7 as a background worker with zero external API dependencies.\n\n"
        "**Available Commands:**\n"
        "🕒 `/time` - Get detailed current date & time variations.\n"
        "⏳ `/timer <seconds>` - Set an isolated focus timer.\n"
        "🔤 `/caps <text>` - Convert any text to capital letters.\n\n"
        "Or just type any text message and I will echo its diagnostic character length!"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns current UTC time elements."""
    now = datetime.now(timezone.utc)
    time_response = (
        "📊 **Current Server Metrics (UTC):**\n"
        f"• Date: `{now.strftime('%Y-%m-%d')}`\n"
        f"• Time (24h): `{now.strftime('%H:%M:%S')}`\n"
        f"• Day of Week: `{now.strftime('%A')}`"
    )
    await update.message.reply_text(time_response, parse_mode="Markdown")

async def caps_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Converts user text to uppercase."""
    if not context.args:
        await update.message.reply_text("Please provide text! Example: `/caps hello world`")
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
        due = float(context.args[0])
        if due <= 0:
            await update.message.reply_text("Please specify a positive number of seconds.")
            return

        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=int(due))
        await update.message.reply_text(f"⏳ Timer successfully set for `{int(due)}` seconds!", parse_mode="Markdown")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: `/timer <seconds>` (e.g., `/timer 60`)", parse_mode="Markdown")

async def echo_diagnostics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echos back text diagnostics metrics."""
    user_text = update.message.text
    response = (
        "📝 **Text Diagnostic Tool**\n"
        f"• Your Text: \"{user_text}\"\n"
        f"• Characters: `{len(user_text)}`"
    )
    await update.message.reply_text(response, parse_mode="Markdown")

async def native_async_main() -> None:
    """
    Explicit, custom loop architecture built to bypass 
    Python 3.14's native polling bugs on isolated platforms.
    """
    if not TOKEN:
        logger.critical("CRITICAL: TELEGRAM_BOT_TOKEN environment variable is missing completely!")
        return

    logger.info("Initializing explicit Async Application context...")
    application = Application.builder().token(TOKEN).build()

    # Handlers Configuration
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("caps", caps_command))
    application.add_handler(CommandHandler("timer", timer_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_diagnostics))

    # Explicit Initialization sequence mapping
    await application.initialize()
    await application.updater.start_polling(drop_pending_updates=True)
    await application.start()
    
    logger.info("🚀 ChronoTask Bot successfully initialized. Listening continuously...")
    
    # Keeps the Render background container permanently running without blocking threads
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        logger.info("Stopping bot processing layers natively...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main() -> None:
    """Executes the custom loop manually using standard loop bindings."""
    try:
        asyncio.run(native_async_main())
    except Exception as e:
        logger.exception(f"Unhandled execution event occurred: {e}")

if __name__ == "__main__":
    main()
