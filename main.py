import asyncio
import logging

from aiogram import Dispatcher
from utils.bot_instance import bot  # Импортируем бота из нашего файла
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем конфиг и функцию создания таблиц
from database import create_tables, update_onboarding_table, update_payments_table  # ДОБАВЛЯЕМ update_onboarding_table

from utils.notifications import check_expiring_access
from utils.reminders import send_pdf_followup
from utils.reminders import send_reminders
from utils.reminders import send_nutrition_reminders

# Импортируем все роутеры (обработчики)
from handlers.start import router as start_router
from handlers.questionnaire import router as questionnaire_router
from handlers.common import router as common_router
from handlers.training import router as training_router
from handlers.payment import router as payment_router
from handlers.nutrition import router as nutrition_router
from handlers.exercises import router as exercises_router
from handlers.admin import router as admin_router
from handlers.faq import router as faq_router
from handlers.support import router as support_router
from handlers.progress import router as progress_router
from handlers.onboarding import router as onboarding_router

# Настраиваем логирование, чтобы видеть что происходит
logging.basicConfig(level=logging.INFO)

# Хранилище состояний (FSM) пока храним в оперативной памяти. Для продакшена лучше использовать Redis.
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Функция, которая запускается при старте бота
async def on_startup():
    print("Бот запущен...")
    # Создаем таблицы в базе данных, если они еще не созданы
    await create_tables()

    await update_payments_table()
    
    # ДОБАВЛЯЕМ ЭТУ СТРОКУ - обновляем таблицу для новой анкеты
    await update_onboarding_table()
    
    # ДОБАВЛЯЕМ ОБНОВЛЕНИЕ ТАБЛИЦЫ PAYMENTS
    await update_payments_table()
    
    # Запускаем фоновую задачу для уведомлений
    asyncio.create_task(check_expiring_access())
    asyncio.create_task(send_reminders())
    asyncio.create_task(send_nutrition_reminders())
    asyncio.create_task(send_pdf_followup())
    
    # ЗАКОММЕНТИРУЕМ автоматическую инициализацию FAQ
    # from utils.init_faq import init_faq_data
    # await init_faq_data()

# Функция, которая запускается при остановке бота
async def on_shutdown():
    print("Бот остановлен.")
    # Здесь можно добавить логику очистки ресурсов

# Главная функция
async def main():
    # Регистрируем роутеры в диспетчере
    dp.include_router(onboarding_router)
    dp.include_router(questionnaire_router)
    dp.include_router(training_router)
    dp.include_router(progress_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(common_router)
    dp.include_router(payment_router)
    dp.include_router(nutrition_router)
    dp.include_router(exercises_router)
    dp.include_router(faq_router)

    # Регистрируем функции, которые выполнятся при старте и остановке
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Запускаем опрос серверов Telegram
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

# Точка входа. Запускаем главную асинхронную функцию.
if __name__ == "__main__":
    asyncio.run(main())