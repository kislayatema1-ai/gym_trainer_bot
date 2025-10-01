import asyncio
from datetime import datetime, timedelta
from database import get_users_with_active_access, get_last_progress_date
from utils.bot_instance import bot

async def send_reminders():
    while True:
        try:
            now = datetime.now()
            
            # Напоминания о взвешивании (каждую пятницу в 9:00)
            if now.weekday() == 4 and now.hour == 9 and now.minute == 0:  # Пятница 9:00
                active_users = await get_users_with_active_access()
                for user in active_users:
                    user_id, username, full_name, access_until = user
                    last_progress = await get_last_progress_date(user_id)
                    
                    if not last_progress or (datetime.now() - datetime.fromisoformat(last_progress)).days > 6:
                        try:
                            await bot.send_message(
                                user_id,
                                "⏰ *Напоминание:* не забудьте внести вес на этой неделе! 📈\n\n"
                                "Используйте раздел «📊 Прогресс» → «📈 Добавить вес»"
                            )
                        except Exception as e:
                            print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
            
            # Напоминания о тренировках (пн, ср, пт в 8:00)
            if now.weekday() in [0, 2, 4] and now.hour == 8 and now.minute == 0:  # Пн, Ср, Пт 8:00
                active_users = await get_users_with_active_access()
                for user in active_users:
                    user_id, username, full_name, access_until = user
                    try:
                        await bot.send_message(
                            user_id,
                            "💪 *Сегодня день тренировки!* Не пропускайте! 🏋️\n\n"
                            "Удачи на тренировке! 💥"
                        )
                    except Exception as e:
                        print(f"Не удалось отправить напоминание о тренировке пользователю {user_id}: {e}")
            
            # Проверяем раз в минуту (вместо раз в день для тестирования)
            await asyncio.sleep(60)  # 60 секунд для тестирования
            
        except Exception as e:
            print(f"Error in reminders: {e}")
            await asyncio.sleep(300)  # Ждем 5 минут при ошибке

async def send_nutrition_reminders():
    while True:
        try:
            # Проверяем пользователей для follow-up
            from database import get_users_for_followup
            users_to_followup = await get_users_for_followup()
            
            for user_id in users_to_followup:
                try:
                    await bot.send_message(
                        user_id,
                        "🍎 Привет! Напоминаю о предложении персонального плана питания!\n\n"
                        "Хочешь чтобы я разработал для тебя индивидуальный рацион?",
                        reply_markup=get_nutrition_reminder_keyboard()
                    )
                    
                    # Обновляем дату следующего вопроса
                    next_date = datetime.datetime.now() + datetime.timedelta(hours=48)
                    from database import update_onboarding_data
                    await update_onboarding_data(user_id, next_question_date=next_date.isoformat())
                    
                except Exception as e:
                    print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
            
            # Проверяем раз в час
            await asyncio.sleep(3600)
            
        except Exception as e:
            print(f"Error in nutrition reminders: {e}")
            await asyncio.sleep(300)

async def send_pdf_followup():
    while True:
        try:
            # Проверяем пользователей для follow-up через 24 часа
            from database import get_users_for_followup
            users_to_followup = await get_users_for_followup()
            
            for user_id in users_to_followup:
                try:
                    await bot.send_message(
                        user_id,
                        "🍎 Привет! Напоминаю о файле с рационом!\n\n"
                        "Воспользовался ли ты подарком? Получилось ли применить рекомендации?",
                        reply_markup=get_pdf_followup_keyboard()
                    )
                    
                    # Обновляем дату следующего вопроса
                    from database import update_onboarding_data
                    await update_onboarding_data(user_id, next_question_date=None)  # Больше не спрашиваем
                    
                except Exception as e:
                    print(f"Не удалось отправить напоминание пользователю {user_id}: {e}")
            
            # Проверяем раз в час
            await asyncio.sleep(3600)
            
        except Exception as e:
            print(f"Error in PDF followup: {e}")
            await asyncio.sleep(300)

def get_pdf_followup_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, воспользовался", callback_data="pdf_followup_yes")
    builder.button(text="❌ Нет, не воспользовался", callback_data="pdf_followup_no")
    builder.button(text="📞 Нужна помощь", callback_data="pdf_followup_help")
    builder.adjust(1)
    return builder.as_markup()

def get_nutrition_reminder_keyboard():
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, хочу план питания!", callback_data="nutrition_plan_yes")
    builder.button(text="❌ Нет, спасибо", callback_data="nutrition_plan_no")
    return builder.as_markup()