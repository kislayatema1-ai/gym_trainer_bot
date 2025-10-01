from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.google_sheets import sheets_manager
from database import get_training_sheet_url, save_training_sheet_url
from keyboards.main_menu import get_training_keyboard, get_main_keyboard
from utils.bot_instance import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

class TrainingStates(StatesGroup):
    waiting_for_exercise_data = State()

# Обработчик кнопки "🏋️ Тренировки" из Reply-клавиатуры
@router.message(F.text == "🏋️ Тренировки")
async def handle_training_message(message: Message):
    """Обработка нажатия кнопки Тренировки из главного меню"""
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    # Проверяем есть ли у пользователя таблица
    sheet_url = await get_training_sheet_url(user_id)
    
    if not sheet_url:
        # Создаем новую таблицу
        sheet_url = sheets_manager.create_training_spreadsheet(user_id, user_name)
        if sheet_url:
            await save_training_sheet_url(user_id, sheet_url)
    
    text = (
        "🏋️ *Система тренировок*\n\n"
        "📊 Ваши тренировки хранятся в персональной Google таблице\n\n"
        "*Что вы можете делать:*\n"
        "• 📝 Записывать веса и подходы в реальном времени\n"
        "• 📈 Отслеживать прогресс по графикам\n"
        "• 🔄 Синхронизироваться с тренером\n"
        "• 💪 Получать персональные программы\n\n"
        "*Тренер видит все ваши результаты сразу после записи!*"
    )
    
    await message.answer(text, reply_markup=get_training_keyboard())

# Обработчик inline-кнопок тренировок
@router.callback_query(F.data == "training_my_sheet")
async def training_my_sheet(callback: CallbackQuery):
    """Показывает ссылку на таблицу пользователя"""
    user_id = callback.from_user.id
    sheet_url = await get_training_sheet_url(user_id)
    
    if sheet_url:
        text = (
            "📊 *Ваша таблица тренировок*\n\n"
            f"🔗 *Ссылка:* {sheet_url}\n\n"
            "*Как использовать:*\n"
            "1. Откройте таблицу по ссылке выше\n"
            "2. Найдите свой день тренировки\n"
            "3. Записывайте веса после каждого подхода\n"
            "4. Тренер увидит изменения сразу!\n\n"
            "*💡 Совет:* Добавьте ссылку в закладки браузера"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Открыть таблицу", url=sheet_url)
        builder.button(text="🔙 Назад", callback_data="training_back")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(
            "❌ Таблица не найдена. Нажмите 'Создать таблицу'",
            reply_markup=get_training_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "training_create_sheet")
async def training_create_sheet(callback: CallbackQuery):
    """Создание новой таблицы тренировок"""
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    
    await callback.message.edit_text("🔄 Создаю вашу персональную таблицу тренировок...")
    
    sheet_url = sheets_manager.create_training_spreadsheet(user_id, user_name)
    
    if sheet_url:
        await save_training_sheet_url(user_id, sheet_url)
        
        text = (
            "✅ *Таблица создана!*\n\n"
            "📊 Ваша персональная таблица готова к использованию!\n\n"
            "*Что теперь делать:*\n"
            "1. Откройте таблицу по кнопке ниже\n"
            "2. Тренер уже добавил вашу программу\n"
            "3. Записывайте веса после каждого подхода\n"
            "4. Тренер будет отслеживать ваш прогресс\n\n"
            "*🔒 Доступ есть только у вас и тренера!*"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Открыть таблицу", url=sheet_url)
        builder.button(text="💪 Понятно", callback_data="training_back")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(
            "❌ Не удалось создать таблицу. Пожалуйста, свяжитесь с тренером.",
            reply_markup=get_training_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "training_help")
async def training_help(callback: CallbackQuery):
    """Инструкция по использованию системы тренировок"""
    text = (
        "📖 *Инструкция по системе тренировок*\n\n"
        "*1. 📊 Ваша таблица:*\n"
        "• У каждого пользователя своя личная таблица\n"
        "• Тренер заранее заполняет программу тренировок\n"
        "• Вы видите только свои данные\n\n"
        "*2. 📝 Как записывать:*\n"
        "• Откройте таблицу перед тренировкой\n"
        "• Найдите упражнения на нужный день\n"
        "• В столбцах 'Подход 1-4' записывайте вес\n"
        "• В 'Примечания' можно писать комментарии\n\n"
        "*3. 👁️‍🗨️ Контроль тренера:*\n"
        "• Тренер видит все изменения в реальном времени\n"
        "• Может корректировать программу онлайн\n"
        "• Следит за вашим прогрессом\n\n"
        "*4. 💡 Советы:*\n"
        "• Сохраните ссылку в закладках\n"
        "• Используйте таблицу с телефона во время тренировки\n"
        "• Не удаляйте и не меняйте названия упражнений"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Открыть мою таблицу", callback_data="training_my_sheet")
    builder.button(text="🔙 Назад", callback_data="training_back")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "training_progress")
async def training_progress(callback: CallbackQuery):
    """Показывает прогресс тренировок"""
    user_id = callback.from_user.id
    
    text = (
        "📈 *Ваш прогресс тренировок*\n\n"
        "*Последние результаты:*\n"
        "• 🏋️ Жим лежа: 80кг × 8 повт. (+5кг за месяц)\n"
        "• 🦵 Приседания: 100кг × 6 повт. (+10кг)\n"
        "• 📊 Становая: 120кг × 4 повт. (+15кг)\n\n"
        "*📅 Программа на неделю:*\n"
        "• Пн: Грудь, Трицепс\n"
        "• Ср: Спина, Бицепс\n"
        "• Пт: Ноги, Плечи\n\n"
        "*📊 Для детальной статистики откройте таблицу*"
    )
    
    sheet_url = await get_training_sheet_url(user_id)
    builder = InlineKeyboardBuilder()
    
    if sheet_url:
        builder.button(text="📊 Открыть таблицу", url=sheet_url)
    builder.button(text="🔄 Обновить", callback_data="training_progress")
    builder.button(text="🔙 Назад", callback_data="training_back")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "training_start")
async def training_start(callback: CallbackQuery):
    """Начало тренировки"""
    user_id = callback.from_user.id
    sheet_url = await get_training_sheet_url(user_id)
    
    if sheet_url:
        text = (
            "💪 *Начинаем тренировку!*\n\n"
            "*План на сегодня:*\n"
            "• Разминка: 5-10 минут\n"
            "• Основные упражнения (см. таблицу)\n"
            "• Заминка: 5 минут\n\n"
            "*📝 Не забудьте:*\n"
            "• Записывать веса в таблицу\n"
            "• Следить за техникой\n"
            "• Пить воду во время тренировки\n\n"
            "📊 *Откройте таблицу для просмотра упражнений*"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Открыть таблицу", url=sheet_url)
        builder.button(text="✅ Начал тренировку", callback_data="training_back")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(
            "❌ Сначала создайте таблицу тренировок",
            reply_markup=get_training_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "training_back")
async def training_back(callback: CallbackQuery):
    """Возврат в меню тренировок"""
    user_id = callback.from_user.id
    user_name = callback.from_user.full_name
    
    sheet_url = await get_training_sheet_url(user_id)
    
    text = (
        "🏋️ *Система тренировок*\n\n"
        "📊 Ваши тренировки хранятся в персональной Google таблице\n\n"
        "*Доступные действия:*"
    )
    
    await callback.message.edit_text(text, reply_markup=get_training_keyboard())
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🔙 Возвращаемся в главное меню...\n\n"
        "Используйте кнопки ниже для навигации:"
    )
    await callback.message.answer(
        "🏠 *Главное меню*", 
        reply_markup=get_main_keyboard()
    )
    await callback.answer()