import pyromod.listen
from config import Config
from pyrogram import Client, idle
import asyncio
import threading
from logger import LOGGER
from modules.retasks import recover_incomplete_batches
from modules.scheduler import start_daily_schedulers
from flask import Flask

# ---------- Flask app for health checks ----------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    # Run Flask on port 10000 (Render default) or 5000 if local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ---------- Bot ----------
async def main():
    bot = Client(
        "Bot",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=30,
        plugins=dict(root="plugins"),
        workers=1000,
    )
    await bot.start()
    bot_info = await bot.get_me()
    LOGGER.info(f"<--- @{bot_info.username} Started --->")
    asyncio.create_task(recover_incomplete_batches(bot))
    asyncio.create_task(start_daily_schedulers(bot))
    LOGGER.info("Daily update schedulers started")
    await idle()

if __name__ == "__main__":
    # Start Flask in a background thread
    import os
    threading.Thread(target=run_flask, daemon=True).start()
    # Run the bot's event loop
    asyncio.get_event_loop().run_until_complete(main())
    LOGGER.info("<--- Bot Stopped --->")
