# utils/notifications.py
import asyncio
from datetime import datetime
from database import get_users_with_expiring_access
from .bot_instance import bot  # Импортируем бота из нашего нового файла

async def check_expiring_access():
    while True:
        try:
            users = await get_users_with_expiring_access(3)  # За 3 дня
            for user in users:
                user_id, username, full_name, access_until = user
                message = (
                    f"⚠️ Через 3 дня заканчивается ваш доступ к боту ({access_until}).\n\n"
                    f"Не прерывайте свой прогресс! Для продления зайдите в раздел «💳 Оплата / Доступ»."
                )
                await bot.send_message(chat_id=user_id, text=message)
            
            # Проверяем раз в день
            await asyncio.sleep(86400)  # 24 часа
        except Exception as e:
            print(f"Error in notification system: {e}")
            await asyncio.sleep(3600)  # Ждем час при ошибке