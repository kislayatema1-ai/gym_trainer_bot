from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()

# ЗАМЕНИТЕ ЭТИ ДАННЫЕ НА СВОИ!
ADMIN_USERNAME = "@Daglas99"  # Например: "@ivan_trainer"
ADMIN_CONTACT = "+375298137789"   # Ваш номер телефона

# Обработчик для кнопок "Связь с тренером"
@router.callback_query(lambda c: c.data == "support_contact")
async def handle_support_contact(callback: CallbackQuery):
    contact_text = (
        "📞 *Связь с тренером*\n\n"
        "Вы можете написать мне напрямую:\n\n"
        f"👤 Telegram: {ADMIN_USERNAME}\n"
        f"📱 Телефон: {ADMIN_CONTACT}\n\n"
        "Отвечаю в течение 24 часов! 🕐"
    )
    
    await callback.message.answer(contact_text)
    await callback.answer()

# Обработчик для текстовой кнопки "Связь с тренером" 
@router.message(lambda m: m.text == "📞 Связь с тренером")
async def handle_support_text(message: Message):
    contact_text = (
        "📞 *Связь с тренером*\n\n"
        "Вы можете написать мне напрямую:\n\n"
        f"👤 Telegram: {ADMIN_USERNAME}\n"
        f"📱 Телефон: {ADMIN_CONTACT}\n\n"
        "Я всегда стараюсь ответить вам в ближайшее время! 🕐"
    )
    
    await message.answer(contact_text)