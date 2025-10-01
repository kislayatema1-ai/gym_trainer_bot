# utils/bot_instance.py
from aiogram import Bot
from config import config

# Создаем экземпляр бота здесь, чтобы избежать circular imports
bot = Bot(token=config.BOT_TOKEN)