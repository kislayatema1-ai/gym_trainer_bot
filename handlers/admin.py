from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import get_all_users, get_users_with_expiring_access, get_pending_payments, get_pending_calorie_requests, get_stats, add_user_access, update_payment_status, update_calorie_request_status, delete_user, get_detailed_stats, search_users
from keyboards.admin_menu import get_admin_keyboard, get_admin_users_keyboard, get_admin_payments_keyboard, get_admin_decision_keyboard
from keyboards.admin_advanced import get_admin_advanced_keyboard, get_admin_users_advanced_keyboard, get_admin_confirm_delete_keyboard
from utils.bot_instance import bot
import datetime

router = Router()

# Состояния для админ-действий
class AdminAddAccess(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_days = State()

class AdminStates(StatesGroup):
    waiting_for_delete_user_id = State()
    waiting_for_search_term = State()


# Команда для открытия админ-панели
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("У вас нет доступа к админ-панели.")
        return
    
    stats = await get_stats()
    text = (
        "👑 *Расширенная админ-панель*\n\n"
        f"📊 Статистика:\n"
        f"• Всего пользователей: {stats['total_users']}\n"
        f"• Активных пользователей: {stats['active_users']}\n"
        f"• Платежей на проверке: {stats['pending_payments']}\n"
        f"• Запросов калорий: {stats['pending_calories']}\n\n"
        "Выберите раздел для управления:"
    )
    await message.answer(text, reply_markup=get_admin_advanced_keyboard())

# Навигация назад
@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    stats = await get_stats()
    text = (
        "👑 *Расширенная админ-панель*\n\n"
        f"📊 Статистика:\n"
        f"• Всего пользователей: {stats['total_users']}\n"
        f"• Активных пользователей: {stats['active_users']}\n"
        f"• Платежей на проверке: {stats['pending_payments']}\n"
        f"• Запросов калорий: {stats['pending_calories']}\n\n"
        "Выберите раздел для управления:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_advanced_keyboard())
    await callback.answer()

# Управление пользователями (расширенное)
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    await callback.message.edit_text("👥 *Управление пользователями*:\n\nВыберите действие:", reply_markup=get_admin_users_advanced_keyboard())
    await callback.answer()

# Удаление пользователя
@router.callback_query(F.data == "admin_users_delete")
async def admin_users_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID пользователя для удаления (или 'отмена' для отмены):")
    await state.set_state(AdminStates.waiting_for_delete_user_id)
    await callback.answer()

@router.message(AdminStates.waiting_for_delete_user_id, F.text)
async def process_delete_user_id(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'cancel', 'нет']:
        await message.answer("❌ Удаление отменено.")
        await state.clear()
        return
    
    try:
        user_id = int(message.text)
        # Проверяем существование пользователя
        users = await get_all_users()
        user_exists = any(user[0] == user_id for user in users)
        
        if user_exists:
            await message.answer(
                f"⚠️ Вы уверены, что хотите удалить пользователя с ID {user_id}?\n\n"
                "Это действие нельзя отменить! Будут удалены все данные пользователя.",
                reply_markup=get_admin_confirm_delete_keyboard(user_id)
            )
        else:
            await message.answer("❌ Пользователь с таким ID не найден.")
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный ID пользователя (число):")

@router.callback_query(F.data == "admin_users_list")
async def admin_users_list(callback: CallbackQuery):
    users = await get_all_users()
    text = "📋 *Список пользователей:*\n\n"
    for user in users:
        user_id, username, full_name, access_until = user
        status = "✅ Активен" if access_until and datetime.datetime.strptime(access_until, '%Y-%m-%d').date() >= datetime.date.today() else "❌ Не активен"
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n📅 Доступ: {access_until}\n{status}\n────────────\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_users_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_delete_confirm_"))
async def admin_delete_confirm(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_delete_confirm_", ""))
    
    try:
        await delete_user(user_id)
        await callback.message.edit_text(f"✅ Пользователь с ID {user_id} успешно удален!")
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка при удалении пользователя: {e}")
    
    await callback.answer()

# Детальная статистика
@router.callback_query(F.data == "admin_stats_detailed")
async def admin_stats_detailed(callback: CallbackQuery):
    stats = await get_detailed_stats()
    
    text = (
        "📊 *Детальная статистика:*\n\n"
        f"👥 Пользователи:\n"
        f"• Всего: {stats['total_users']}\n"
        f"• Активных: {stats['active_users']}\n"
        f"• Новых за 30 дней: {stats['new_users_30d']}\n\n"
        f"💰 Финансы:\n"
        f"• Платежей за 30 дней: {stats['recent_payments']}\n"
        f"• Доход за 30 дней: {stats['recent_revenue']} BYN\n\n"
        f"📅 Дата: {datetime.date.today().strftime('%d.%m.%Y')}"
    )
    
    await callback.message.edit_text(text, reply_markup=get_admin_advanced_keyboard())
    await callback.answer()

# Все команды админа
@router.callback_query(F.data == "admin_commands")
async def admin_commands(callback: CallbackQuery):
    commands_text = (
        "📋 *Все команды админа:*\n\n"
        "• /admin - Открыть админ-панель\n"
        "• /stats - Статистика бота\n"
        "• /users - Список пользователей\n"
        "• /payments - Платежи на проверке\n"
        "• /calorierequests - Запросы калорий\n"
        "• /support - Сообщения поддержки\n"
        "• /answer <id> <текст> - Ответить на сообщение\n"
        "• /setcalories <id> <калории> <белки> <жиры> <углеводы> - Установить нормы\n"
        "• /addfaqcategory <название> <описание> - Добавить категорию FAQ\n"
        "• /addfaq - Добавить вопрос в FAQ\n"
        "• /addyoutube - Добавить YouTube видео\n"
        "• /broadcast <текст> - Рассылка всем пользователям\n\n"
        "⚙️ *Для доступа к полному функционалу используйте админ-панель*"
    )
    
    await callback.message.edit_text(commands_text, reply_markup=get_admin_advanced_keyboard())
    await callback.answer()

# Добавляем команду /broadcast для рассылки
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        await message.answer("Использование: /broadcast <текст рассылки>")
        return
    
    broadcast_text = parts[1]
    users = await get_all_users()
    
    success = 0
    failed = 0
    
    for user in users:
        user_id, username, full_name, access_until = user
        try:
            await bot.send_message(user_id, f"📢 *Рассылка от тренера:*\n\n{broadcast_text}")
            success += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            failed += 1
    
    await message.answer(f"✅ Рассылка завершена!\n• Успешно: {success}\n• Не удалось: {failed}")

# Поиск пользователя
@router.callback_query(F.data == "admin_users_search")
async def admin_users_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 Введите ID, username или имя пользователя для поиска:")
    await state.set_state(AdminStates.waiting_for_search_term)
    await callback.answer()

@router.message(AdminStates.waiting_for_search_term, F.text)
async def process_search_term(message: Message, state: FSMContext):
    search_term = message.text
    results = await search_users(search_term)
    
    if not results:
        await message.answer("❌ Пользователи не найдены.")
        await state.clear()
        return
    
    text = "🔍 *Результаты поиска:*\n\n"
    for user in results:
        user_id, username, full_name, access_until = user
        status = "✅ Активен" if access_until and datetime.datetime.strptime(access_until, '%Y-%m-%d').date() >= datetime.date.today() else "❌ Не активен"
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n📅 Доступ: {access_until}\n{status}\n────────────\n"
    
    await message.answer(text)
    await state.clear()

@router.callback_query(F.data == "admin_users_expiring")
async def admin_users_expiring(callback: CallbackQuery):
    users = await get_users_with_expiring_access(7)  # Пользователи с истекающим доступом (7 дней)
    if not users:
        await callback.message.edit_text("Нет пользователей с истекающим доступом.", reply_markup=get_admin_users_keyboard())
        await callback.answer()
        return
    
    text = "⏰ *Пользователи с истекающим доступом:*\n\n"
    for user in users:
        user_id, username, full_name, access_until = user
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n📅 Доступ до: {access_until}\n────────────\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_users_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_users_add_access")
async def admin_users_add_access(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ID пользователя, которому нужно добавить доступ:")
    await state.set_state(AdminAddAccess.waiting_for_user_id)
    await callback.answer()

@router.message(AdminAddAccess.waiting_for_user_id, F.text)
async def process_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("Введите количество дней для добавления:")
        await state.set_state(AdminAddAccess.waiting_for_days)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя (число):")

@router.message(AdminAddAccess.waiting_for_days, F.text)
async def process_days(message: Message, state: FSMContext):
    try:
        days = int(message.text)
        data = await state.get_data()
        user_id = data['user_id']
        
        new_access_date = await add_user_access(user_id, days)
        
        await message.answer(f"✅ Пользователю {user_id} добавлено {days} дней доступа. Новый срок: {new_access_date}")
        
        # Уведомляем пользователя
        user_text = f"🎉 Ваш доступ был продлен на {days} дней! Новый срок: {new_access_date}"
        await bot.send_message(chat_id=user_id, text=user_text)
        
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество дней (число):")

# Управление платежами
@router.callback_query(F.data == "admin_payments")
async def admin_payments(callback: CallbackQuery):
    await callback.message.edit_text("💰 *Управление платежами*:\n\nВыберите действие:", reply_markup=get_admin_payments_keyboard())
    await callback.answer()

@router.callback_query(F.data == "admin_payments_active")
async def admin_payments_active(callback: CallbackQuery):
    payments = await get_pending_payments()
    if not payments:
        await callback.message.edit_text("Нет платежей на проверке.", reply_markup=get_admin_payments_keyboard())
        await callback.answer()
        return
    
    text = "🔄 *Платежи на проверке:*\n\n"
    for payment in payments:
        user_id, username, full_name, screenshot_id, date = payment
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n📅 Дата: {datetime.datetime.fromisoformat(date).strftime('%d.%m.%Y %H:%M')}\n────────────\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_payments_keyboard())
    await callback.answer()

# Управление запросами калорий
@router.callback_query(F.data == "admin_calories")
async def admin_calories(callback: CallbackQuery):
    requests = await get_pending_calorie_requests()
    if not requests:
        await callback.message.edit_text("Нет запросов на расчет калорий.", reply_markup=get_admin_keyboard())
        await callback.answer()
        return
    
    text = "📋 *Запросы на расчет калорий:*\n\n"
    for req in requests:
        request_id, user_id, full_name, username, age, weight, height, gender, activity, goal, created = req
        text += f"👤 {full_name} (@{username})\n🆔 ID: {user_id}\n📊 Возраст: {age}, Вес: {weight}кг, Рост: {height}см\n🎯 Цель: {goal}\n────────────\n"
    
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

# Статистика
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    stats = await get_stats()
    text = (
        "📊 *Статистика бота:*\n\n"
        f"• Всего пользователей: {stats['total_users']}\n"
        f"• Активных пользователей: {stats['active_users']}\n"
        f"• Неактивных пользователей: {stats['total_users'] - stats['active_users']}\n"
        f"• Платежей на проверке: {stats['pending_payments']}\n"
        f"• Запросов калорий: {stats['pending_calories']}\n\n"
        f"📅 Дата: {datetime.date.today().strftime('%d.%m.%Y')}"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    await callback.answer()

@router.message(Command("initfaq"))
async def cmd_init_faq(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    try:
        from utils.init_faq import init_faq_data
        await init_faq_data()
        await message.answer("✅ FAQ данные переинициализированы!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при инициализации FAQ: {e}")