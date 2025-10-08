from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.main_menu import get_main_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import get_access_until

router = Router()

# Обработчик команды /check_access
@router.message(Command('check_access'))
async def cmd_check_access(message: Message):
    user_id = message.from_user.id
    access_until = await get_access_until(user_id)
    await message.answer(f"Ваш доступ активен до: *{access_until}*", parse_mode="Markdown")

@router.message(F.text == "💳 Оплата / Доступ")
async def show_payment_menu(message: Message):
    from keyboards.main_menu import get_payment_keyboard
    await message.answer(
        "💳 *Оплата / Доступ*\n\n"
        "Выберите действие:",
        reply_markup=get_payment_keyboard()
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    from keyboards.main_menu import get_main_keyboard
    
    # Удаляем старое сообщение с Inline-меню
    await callback.message.delete()
    
    # Отправляем новое сообщение с главным меню
    await callback.message.answer(
        "🏠 *Главное меню*\n\n"
        "👇 Выберите раздел:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@router.message(Command("users"))
async def cmd_users(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    from database import get_all_users
    users = await get_all_users()
    
    text = "👥 *Список пользователей:*\n\n"
    for user in users[:10]:  # Первые 10 пользователей
        user_id, username, full_name, access_until = user
        status = "✅ Активен" if access_until and datetime.datetime.strptime(access_until, '%Y-%m-%d').date() >= datetime.date.today() else "❌ Не активен"
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n{status}\n────────────\n"
    
    if len(users) > 10:
        text += f"\n... и еще {len(users) - 10} пользователей"
    
    await message.answer(text)

@router.message(F.text == "🥗 Питание")
async def show_nutrition_menu(message: Message):
    from keyboards.main_menu import get_nutrition_keyboard
    await message.answer(
        "🥗 *Питание*\n\n"
        "Выберите раздел:",
        reply_markup=get_nutrition_keyboard()
    )

@router.message(F.text == "📊 Прогресс")
async def show_progress_menu(message: Message):
    from keyboards.main_menu import get_progress_keyboard
    await message.answer(
        "📊 *Прогресс*\n\n"
        "Выберите действие:",
        reply_markup=get_progress_keyboard()
    )

@router.message(F.text == "📚 Упражнения")
async def show_exercises_menu(message: Message):
    from keyboards.main_menu import get_exercises_keyboard
    await message.answer(
        "📚 *Упражнения*\n\n"
        "Выберите раздел:",
        reply_markup=get_exercises_keyboard()
    )

@router.message(F.text == "❓ FAQ")
async def show_faq_menu(message: Message):
    from keyboards.main_menu import get_faq_keyboard
    await message.answer(
        "❓ *Частые вопросы*\n\n"
        "Выберите раздел:",
        reply_markup=get_faq_keyboard()
    )

@router.message(F.text == "🏋️ Тренировки")
async def show_training_menu(message: Message):
    from keyboards.main_menu import get_training_main_keyboard
    await message.answer(
        "🏋️ *Тренировки*\n\n"
        "Выберите действие:",
        reply_markup=get_training_main_keyboard()
    )