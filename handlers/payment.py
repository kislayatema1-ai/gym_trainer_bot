import asyncio
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from database import add_payment, update_payment_status, update_user_access, get_pending_payments, get_access_until
from keyboards.main_menu import get_payment_keyboard, get_paid_button, get_admin_payment_decision_kb

# Создаем роутер
router = Router()

# Создаем Машину Состояний (FSM) для отслеживания шага оплаты
class PaymentState(StatesGroup):
    waiting_for_screenshot = State()

# Обработчик кнопки "Оплатить абонемент"
@router.callback_query(F.data == "pay_subscription")
async def process_payment(callback: CallbackQuery):
    payment_text = (
        "💳 *ОПЛАТА АБОНЕМЕНТА*\n\n"
        "Для продления доступа, пожалуйста, совершите перевод на карту:\n\n"
        "*Номер карты:* `1111 2222 3333 4444`\n"  # ЗАМЕНИТЕ НА СВОЮ КАРТУ!
        "*Получатель:* Иван Иванов\n"             # ЗАМЕНИТЕ НА СВОЕ ИМЯ!
        "*Сумма:* 100 BYN (за 4 недели)\n\n"
        "⚠️ *В комментарии к переводу ОБЯЗАТЕЛЬНО укажите:*\n"
        "— Ваш номер телефона\n"
        "— Или ваше Имя и Фамилию\n\n"
        "После совершения оплаты нажмите кнопку «✅ Я оплатил(а)» ниже и загрузите скриншот чека."
    )
    await callback.message.edit_text(payment_text, reply_markup=get_paid_button())
    await callback.answer()

# Обработчик кнопки "Я оплатил(а)" - запускаем состояние ожидания скриншота
@router.callback_query(F.data == "i_paid")
async def start_waiting_for_screenshot(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отлично! Теперь, пожалуйста, отправьте одним сообщением *скриншот* или *фотографию* чека из банковского приложения.")
    # Устанавливаем состояние для этого пользователя
    await state.set_state(PaymentState.waiting_for_screenshot)
    await callback.answer()

# Обработчик скриншота, который сработает только в нужном состоянии
@router.message(PaymentState.waiting_for_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Сохраняем file_id самого большого (качественного) изображения
    screenshot_id = message.photo[-1].file_id

    # Сохраняем информацию о платеже в базу
    await add_payment(user_id, screenshot_id)

    # Сообщаем пользователю
    await message.answer("Скриншот получен и передан тренеру на проверку. Вы получите уведомление, как только доступ будет активирован. Обычно это занимает несколько часов. Спасибо!")

    # Сбрасываем состояние
    await state.clear()

    # --- ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ АДМИНУ ---
    admin_text = (
        f"🔄 *НОВЫЙ ПЛАТЕЖ НА ПРОВЕРКУ*\n\n"
        f"*Клиент:* {message.from_user.full_name} (@{message.from_user.username})\n"
        f"*User ID:* `{user_id}`\n"
        f"*Дата и время:* {message.date.strftime('%d.%m.%Y, %H:%M')}"
    )
    # Отправляем админу текст и скриншот
    from utils.bot_instance import bot  # Импортируем бота отсюда (осторожно с циклическими импортами)
    await bot.send_photo(chat_id=config.ADMIN_ID, photo=screenshot_id, caption=admin_text, reply_markup=get_admin_payment_decision_kb(user_id))

# Обработчик для админа: Подтвердить платеж
@router.callback_query(F.data.startswith("approve_"))
async def admin_approve_payment(callback: CallbackQuery):
    # Извлекаем данные: approve_123456789_full -> (123456789, 'full')
    parts = callback.data.split("_")
    user_id = int(parts[1])
    product_type = parts[2] if len(parts) > 2 else 'full'
    admin_id = callback.from_user.id

    if admin_id != config.ADMIN_ID:
        await callback.answer("У вас нет прав для этого действия.")
        return

    # Обновляем статус платежа
    await update_payment_status(user_id, 'approved')
    
    product_type_text = "полное ведение" if product_type == 'full' else "план питания"
    
    if product_type == 'full':
        # Полное ведение - даем полный доступ
        new_access_date = await update_user_access(user_id, 30)
        access_message = f"✅ Ваш платеж подтвержден! Ваш доступ к боту продлен до {new_access_date}."
        
        # ЗАПУСКАЕМ БОЛЬШУЮ АНКЕТУ ТОЛЬКО ДЛЯ ПОЛНОГО ВЕДЕНИЯ
        try:
            from handlers.questionnaire import start_full_questionnaire
            await asyncio.sleep(2)
            await start_full_questionnaire(user_id)
        except Exception as e:
            print(f"Ошибка при запуске анкеты: {e}")
            from utils.bot_instance import bot
            await bot.send_message(chat_id=config.ADMIN_ID, text=f"❌ Ошибка при запуске анкеты для пользователя {user_id}: {e}")
            
    else:
        # План питания - не даем полный доступ
        access_message = "✅ Ваш платеж подтвержден! План питания будет отправлен в течение 24 часов."
        # Здесь можно добавить отправку плана питания

    # Сообщаем админу
    await callback.message.edit_caption(
        caption=f"✅ Платеж от пользователя ID {user_id} *ПОДТВЕРЖДЕН*.\n"
                f"Тип: {product_type_text}\n"
                f"Сумма: {'100' if product_type == 'full' else '25'} BYN"
    )
    await callback.answer("Одобрено!")

    # Сообщаем пользователю
    from utils.bot_instance import bot
    await bot.send_message(chat_id=user_id, text=access_message)

# Обработчик для админа: Отклонить платеж
@router.callback_query(F.data.startswith("deny_"))
async def admin_deny_payment(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[1])
    product_type = parts[2] if len(parts) > 2 else 'full'
    admin_id = callback.from_user.id

    if admin_id != config.ADMIN_ID:
        await callback.answer("У вас нет прав для этого действия.")
        return

    await update_payment_status(user_id, 'denied')
    
    product_type_text = "полное ведение" if product_type == 'full' else "план питания"

    await callback.message.edit_caption(
        caption=f"❌ Платеж от пользователя ID {user_id} *ОТКЛОНЕН*.\n"
                f"Тип: {product_type_text}"
    )
    await callback.answer("Отклонено!")

    user_notification_text = (
        "❌ Ваш платеж не был подтвержден. "
        "Возможно, скриншот нечитаем или платеж не был найден. "
        "Пожалуйста, свяжитесь с тренером через раздел «📞 Связь по оплате»."
    )
    from utils.bot_instance import bot
    await bot.send_message(chat_id=user_id, text=user_notification_text)

# Обработчик кнопки "Проверить мой доступ"
@router.callback_query(F.data == "check_my_access")
async def check_access_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    access_until = await get_access_until(user_id)
    await callback.answer(f"Ваш доступ активен до: {access_until}", show_alert=True)

@router.message(Command('payments'))
async def cmd_payments(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    pending_payments = await get_pending_payments()
    if not pending_payments:
        await message.answer("Нет платежей на проверке.")
        return
    
    text = "📋 Платежи на проверке:\n\n"
    for payment in pending_payments:
        user_id, username, full_name, screenshot_id, date = payment
        text += f"👤 {full_name} (@{username})\n"
        text += f"🆔 ID: {user_id}\n"
        text += f"📅 Дата: {datetime.datetime.fromisoformat(date).strftime('%d.%m.%Y %H:%M')}\n"
        text += f"🔗 Screenshot ID: {screenshot_id}\n"
        text += "─" * 20 + "\n"
    
    await message.answer(text)