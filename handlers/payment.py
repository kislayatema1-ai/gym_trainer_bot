import asyncio
import os
import datetime
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

# Обработчик кнопки "Оплатить абонемент" - показываем выбор периода
@router.callback_query(F.data == "pay_subscription")
async def process_payment(callback: CallbackQuery, state: FSMContext):
    payment_text = (
        "💳 *ОПЛАТА АБОНЕМЕНТА*\n\n"
        "Период: *1 месяц*\n"
        "Сумма: *200 BYN*\n\n"
        "Для продления доступа, пожалуйста, совершите перевод на карту:\n\n"
        "*Номер карты:* `5299 2299 3689 8638`\n"
        "*Сумма:* 200 BYN\n\n"
        "⚠️ *В комментарии к переводу ОБЯЗАТЕЛЬНО укажите:*\n"
        "— Ваш телеграм\n"
        "— Или ваше Имя и Фамилию\n\n"
        "После совершения оплаты нажмите кнопку «✅ Я оплатил(а)» ниже и загрузите скриншот чека."
    )
    
    # Сохраняем данные о периоде в состоянии
    await state.update_data(
        payment_days=30,
        payment_amount=200,
        payment_period="1 месяц"
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

@router.message(PaymentState.waiting_for_screenshot, F.photo)
async def receive_screenshot(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    
    # ДЕТАЛЬНЫЙ ОТЛАДОЧНЫЙ ВЫВОД
    print(f"🔍 DEBUG receive_screenshot:")
    print(f"   User ID: {user_id}")
    print(f"   Все данные состояния: {data}")
    print(f"   payment_days: {data.get('payment_days', 'NOT_FOUND')}")
    print(f"   payment_amount: {data.get('payment_amount', 'NOT_FOUND')}")
    print(f"   payment_period: {data.get('payment_period', 'NOT_FOUND')}")
    
    # Сохраняем file_id самого большого (качественного) изображения
    screenshot_id = message.photo[-1].file_id
    print(f"   Screenshot ID: {screenshot_id}")

    # Определяем тип продукта и параметры
    product_type = data.get('product_type', 'full')
    print(f"   Product type: {product_type}")
    
    if product_type == 'full':
        # Для полного ведения используем данные из состояния
        days = data.get('payment_days', 30)
        amount = data.get('payment_amount', 200)
        period_text = data.get('payment_period', '1 месяц')
        
        print(f"   Сохраняем в БД: days={days}, amount={amount}, period={period_text}")
        
        # Сохраняем информацию о платеже в базу С КОЛИЧЕСТВОМ ДНЕЙ
        await add_payment(user_id, screenshot_id, product_type, days)
        
        # Сообщаем пользователю
        await message.answer("Скриншот получен и передан тренеру на проверку. Вы получите уведомление, как только доступ будет активирован. Обычно это занимает несколько часов. Спасибо!")

        # --- ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ АДМИНУ ---
        admin_text = (
            f"🔄 *НОВЫЙ ПЛАТЕЖ НА ПРОВЕРКУ*\n\n"
            f"*Тип:* Полное ведение\n"
            f"*Клиент:* {message.from_user.full_name} (@{message.from_user.username})\n"
            f"*User ID:* `{user_id}`\n"
            f"*Период:* {period_text}\n"
            f"*Сумма:* {amount} BYN\n"
            f"*Дней доступа:* {days}\n"
            f"*Дата и время:* {message.date.strftime('%d.%m.%Y, %H:%M')}"
        )
        
    else:
        # Для плана питания
        days = 0  # План питания не дает доступ к боту
        amount = 50
        
        # Сохраняем информацию о платеже в базу
        await add_payment(user_id, screenshot_id, product_type, days)
        
        # Сообщаем пользователю
        await message.answer("Скриншот получен и передан тренеру на проверку. Вы получите план питания в течение 24 часов после подтверждения оплаты. Спасибо!")

        # --- ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ АДМИНУ ---
        admin_text = (
            f"🔄 *НОВЫЙ ПЛАТЕЖ НА ПРОВЕРКУ*\n\n"
            f"*Тип:* План тренировок\n"
            f"*Клиент:* {message.from_user.full_name} (@{message.from_user.username})\n"
            f"*User ID:* `{user_id}`\n"
            f"*Сумма:* 50 BYN\n"
            f"*Дата и время:* {message.date.strftime('%d.%m.%Y, %H:%M')}"
        )

    # Сбрасываем состояние
    await state.clear()

    # ДОБАВЛЯЕМ ОТЛАДОЧНЫЙ ВЫВОД ПЕРЕД ОТПРАВКОЙ АДМИНУ
    print(f"DEBUG: Отправка админу - product_type: {product_type}, days: {days}")
    
    # Отправляем админу текст и скриншот
    from utils.bot_instance import bot
    await bot.send_photo(
        chat_id=config.ADMIN_ID, 
        photo=screenshot_id, 
        caption=admin_text, 
        reply_markup=get_admin_payment_decision_kb(user_id, product_type, days)
    )

# Обработчик для админа: Подтвердить платеж
@router.callback_query(F.data.startswith("approve_"))
async def admin_approve_payment(callback: CallbackQuery):
    # Извлекаем данные: approve_123456789_full -> (123456789, 'full')
    parts = callback.data.split("_")
    
    if len(parts) < 3:
        await callback.answer("Ошибка в формате данных платежа")
        return
        
    user_id = int(parts[1])
    product_type = parts[2]  # 'full' или 'nutrition'
    
    # Всегда 30 дней для полного ведения
    days_to_add = 30 if product_type == 'full' else 0
    
    admin_id = callback.from_user.id

    if admin_id != config.ADMIN_ID:
        await callback.answer("У вас нет прав для этого действия.")
        return

    # Обновляем статус платежа
    await update_payment_status(user_id, 'approved')
    
    product_type_text = "полное ведение" if product_type == 'full' else "план питания"
    
    if product_type == 'full':
        # Полное ведение - даем доступ
        new_access_date = await update_user_access(user_id, days_to_add)
        
        # ПРОВЕРЯЕМ, ЕСТЬ ЛИ У ПОЛЬЗОВАТЕЛЯ УЖЕ ДОСТУП
        from database import check_user_access
        has_existing_access = await check_user_access(user_id)
        
        if not has_existing_access:
            # Если это ПЕРВЫЙ доступ - запускаем анкету
            access_message = f"✅ Ваш платеж подтвержден! Ваш доступ к боту продлен до {new_access_date}."
            
            # ЗАПУСКАЕМ БОЛЬШУЮ АНКЕТУ ТОЛЬКО ДЛЯ ПЕРВОГО ДОСТУПА
            try:
                # ИСПРАВЛЕННЫЙ ИМПОРТ - используем правильный путь к анкете
                from handlers.questionnaire import start_full_questionnaire
                await asyncio.sleep(2)
                
                # Отправляем сообщение пользователю
                from utils.bot_instance import bot
                await bot.send_message(chat_id=user_id, text=access_message)
                
                # Запускаем анкету
                await start_full_questionnaire(user_id)
            except Exception as e:
                print(f"Ошибка при запуске анкеты: {e}")
                from utils.bot_instance import bot
                await bot.send_message(chat_id=config.ADMIN_ID, text=f"❌ Ошибка при запуске анкеты для пользователя {user_id}: {e}")
                # Все равно отправляем сообщение пользователю
                await bot.send_message(chat_id=user_id, text=access_message)
        else:
            # Если доступ УЖЕ БЫЛ - просто продлеваем и отправляем сообщение
            access_message = (
                f"✅ Ваш платеж подтвержден!\n\n"
                f"📅 Ваш доступ продлен до: {new_access_date}\n\n"
                f"🏋️ Продолжаем тренировки! Все ваши данные сохранены."
            )
            from utils.bot_instance import bot
            await bot.send_message(chat_id=user_id, text=access_message)

        # Сообщаем админу
        await callback.message.edit_caption(
            caption=f"✅ Платеж от пользователя ID {user_id} *ПОДТВЕРЖДЕН*.\n"
                    f"Тип: {product_type_text}\n"
                    f"Период: 1 месяц\n"
                    f"Сумма: 200 BYN"
        )
        
    else:
        # План питания - отправляем сообщение пользователю
        access_message = "✅ Ваш платеж подтвержден! План питания будет отправлен в течение 24 часов."
        from utils.bot_instance import bot
        await bot.send_message(chat_id=user_id, text=access_message)
        
        # Сообщаем админу
        await callback.message.edit_caption(
            caption=f"✅ Платеж от пользователя ID {user_id} *ПОДТВЕРЖДЕН*.\n"
                    f"Тип: {product_type_text}\n"
                    f"Сумма: 50 BYN"
        )

    await callback.answer("Одобрено!")

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

# Обработчик кнопки "Инструкция по оплате"
@router.callback_query(F.data == "pay_instructions")
async def show_payment_instructions(callback: CallbackQuery):
    instructions_text = (
        "💳 *ИНСТРУКЦИЯ ПО ОПЛАТЕ*\n\n"
        "1. *Нажмите «Оплатить абонемент»*\n"
        "   • Стоимость: 200 BYN за 1 месяц\n\n"
        "2. *Совершите перевод на карту:*\n"
        "   • Номер карты: `5299 2299 3689 8638`\n"
        "3. *В комментарии укажите:*\n"
        "   • Ваш телеграм\n"
        "   • Или ваше Имя и Фамилию\n\n"
        "4. *Отправьте скриншот чека*\n\n"
        "5. *Ожидайте подтверждения*\n"
        "   Обычно это занимает несколько часов\n\n"
        "⚠️ *Важно:*\n"
        "• Сохраняйте скриншот до подтверждения оплаты\n"
        "• При проблемах свяжитесь с тренером через «📞 Связь по оплате»"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить абонемент", callback_data="pay_subscription")
    builder.button(text="◀️ Назад", callback_data="payment_back")
    builder.adjust(1)
    
    await callback.message.edit_text(instructions_text, reply_markup=builder.as_markup())
    await callback.answer()

# Обработчик кнопки "Назад" из инструкции
@router.callback_query(F.data == "payment_back")
async def back_to_payment(callback: CallbackQuery):
    from keyboards.main_menu import get_payment_keyboard
    await callback.message.edit_text(
        "💳 *Оплата / Доступ*\n\n"
        "Выберите действие:",
        reply_markup=get_payment_keyboard()
    )
    await callback.answer()

# Обработчик кнопки "Связь по оплате"
@router.callback_query(F.data == "support_contact")
async def show_support_contact(callback: CallbackQuery):
    contact_text = (
        "📞 *Связь по оплате*\n\n"
        "Если у вас возникли проблемы с оплатой:\n\n"
        f"👤 Telegram: {config.ADMIN_USERNAME}\n"
        f"📱 Телефон: {config.ADMIN_CONTACT}\n\n"
        "⏰ Время ответа: 1-2 часа"
    )
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Вернуться к оплате", callback_data="payment_back")
    builder.adjust(1)
    
    await callback.message.edit_text(contact_text, reply_markup=builder.as_markup())
    await callback.answer()

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

# Команда для админа чтобы вручную запустить анкету
@router.message(Command('start_questionnaire'))
async def cmd_start_questionnaire(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    try:
        # Формат команды: /start_questionnaire <user_id>
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("Использование: /start_questionnaire <user_id>")
            return
        
        user_id = int(parts[1])
        
        # Запускаем анкету
        from handlers.onboarding import start_full_questionnaire
        await start_full_questionnaire(user_id)
        
        await message.answer(f"✅ Анкета запущена для пользователя {user_id}")
        
    except ValueError:
        await message.answer("❌ Неверный формат user_id. Использование: /start_questionnaire <user_id>")
    except Exception as e:
        await message.answer(f"❌ Ошибка при запуске анкеты: {e}")