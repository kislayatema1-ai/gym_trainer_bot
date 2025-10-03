from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from database import add_user, check_user_access
from keyboards.main_menu import (
    get_main_keyboard, 
    get_faq_keyboard, 
    get_exercises_keyboard, 
    get_payment_keyboard, 
    get_nutrition_keyboard, 
    get_progress_keyboard,
    get_training_main_keyboard  # ДОБАВИЛ импорт
)

# Создаем роутер для этой группы обработчиков
router = Router()

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Добавляем пользователя в базу данных
    await add_user(user_id, username, full_name)

    # Проверяем его доступ
    has_access = await check_user_access(user_id)

    welcome_text = (
        f"Привет, {full_name}! 👋\n\n"
        "Я — помощник тренера Анастасии. ❤️\n"
        "Я помогу тебе правильно выполнять упражнения, отслеживать свой прогресс, следить за оплатами и многое другое.\n\n"
        "Хочешь получить примерный план питания на день - вкусно и без голодовок?\n"
    )
    if not has_access:
        welcome_text += "⚠️ *Твой доступ не активен.* Для начала работы необходимо оплатить абонемент в разделе «💳 Оплата / Доступ»."
    else:
        welcome_text += "✅ *Твой доступ активен!* Выбирай раздел ниже и начинай работу!"

    # Отправляем приветствие и главное меню
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

# Обработчик команды /help
@router.message(Command('help'))
async def cmd_help(message: Message):
    help_text = (
        "Список доступных команд и разделов:\n\n"
        "/start - Перезапустить бота\n"
        "/help - Получить справку\n"
        "/check_access - Проверить статус своего доступа\n\n"
        "А также ты можешь пользоваться кнопками меню ниже 👇"
    )
    await message.answer(help_text)

# Обработчик кнопки "Главное меню" (из других разделов)
@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=None)  # Удаляем инлайн-клавиатуру
    await callback.message.answer("Выбери раздел:", reply_markup=get_main_keyboard())
    await callback.answer()

@router.message(F.text == "🥗 Питание")
async def open_nutrition(message: Message):
    await message.answer("Раздел «Питание»:", reply_markup=get_nutrition_keyboard())

# Обработчик текстовой кнопки "Тренировка"
@router.message(F.text == "🏋️ Тренировки")
async def open_training(message: Message):
    has_access = await check_user_access(message.from_user.id)
    if not has_access:
        await message.answer("Раздел «Тренировки» доступен только с активным абонементом.")
        return
    await message.answer("Выбери опцию в разделе «Тренировки»:", reply_markup=get_training_main_keyboard())  # ИСПРАВИЛ опечатку

# Обработчик текстовой кнопки "Оплата / Доступ"
@router.message(F.text == "💳 Оплата / Доступ")
async def open_payment(message: Message):
    await message.answer("Раздел «Оплата / Доступ»:", reply_markup=get_payment_keyboard())

# Обработчик текстовой кнопки "Упражнения"
@router.message(F.text == "📚 Упражнения")
async def open_exercises(message: Message):
    await message.answer("Раздел «Упражнения»:", reply_markup=get_exercises_keyboard())

# Обработчик текстовой кнопки "Прогресс"
@router.message(F.text == "📊 Прогресс")
async def open_progress(message: Message):
    await message.answer("📊 Раздел «Прогресс»:", reply_markup=get_progress_keyboard())

# Обработчик текстовой кнопки "FAQ"
@router.message(F.text == "❓ FAQ")
async def open_faq(message: Message):
    await message.answer("❓ Раздел «FAQ»:", reply_markup=get_faq_keyboard())