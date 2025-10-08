from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Расширенное меню админ-панели
def get_admin_advanced_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"),
        InlineKeyboardButton(text="💰 Финансы и платежи", callback_data="admin_finance"),
        InlineKeyboardButton(text="📊 Детальная статистика", callback_data="admin_stats_detailed"),
        InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="admin_search"),
        InlineKeyboardButton(text="⚙️ Настройки бота", callback_data="admin_settings"),
        InlineKeyboardButton(text="📋 Все команды", callback_data="admin_commands"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")
    )
    builder.adjust(2)
    return builder.as_markup()

# Меню управления пользователями
def get_admin_users_advanced_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_users_list"),
        InlineKeyboardButton(text="⏰ Истекающий доступ", callback_data="admin_users_expiring"),
        InlineKeyboardButton(text="➕ Добавить доступ", callback_data="admin_users_add_access"),
        InlineKeyboardButton(text="🗑️ Удалить пользователя", callback_data="admin_users_delete"),
        InlineKeyboardButton(text="🔍 Поиск по пользователям", callback_data="admin_users_search"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура подтверждения удаления
def get_admin_confirm_delete_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"admin_delete_confirm_{user_id}"),
        InlineKeyboardButton(text="❌ Нет, отмена", callback_data="admin_users")
    )
    return builder.as_markup()