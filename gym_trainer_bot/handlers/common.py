from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database import get_access_until

router = Router()

# Обработчик команды /check_access
@router.message(Command('check_access'))
async def cmd_check_access(message: Message):
    user_id = message.from_user.id
    access_until = await get_access_until(user_id)
    await message.answer(f"Ваш доступ активен до: *{access_until}*", parse_mode="Markdown")

# Добавляем новые команды для админа
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    from database import get_stats
    stats = await get_stats()
    
    text = (
        "📊 *Статистика бота:*\n\n"
        f"• Всего пользователей: {stats['total_users']}\n"
        f"• Активных пользователей: {stats['active_users']}\n"
        f"• Платежей на проверке: {stats['pending_payments']}\n"
        f"• Запросов калорий: {stats['pending_calories']}\n\n"
        f"📅 {datetime.date.today().strftime('%d.%m.%Y')}"
    )
    
    await message.answer(text)

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