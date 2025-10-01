from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню админ-панели
def get_admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"),
        InlineKeyboardButton(text="💰 Платежи на проверке", callback_data="admin_payments"),
        InlineKeyboardButton(text="📋 Запросы калорий", callback_data="admin_calories"),
        InlineKeyboardButton(text="🏋️ Управление тренировками", callback_data="admin_training"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(2)
    return builder.as_markup()

# Меню управления пользователями
def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📋 Список пользователей", callback_data="admin_users_list"),
        InlineKeyboardButton(text="⏰ Истекающий доступ", callback_data="admin_users_expiring"),
        InlineKeyboardButton(text="➕ Добавить доступ", callback_data="admin_users_add_access"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")
    )
    builder.adjust(1)
    return builder.as_markup()

# Меню управления платежами
def get_admin_payments_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔄 Активные платежи", callback_data="admin_payments_active"),
        InlineKeyboardButton(text="📊 История платежей", callback_data="admin_payments_history"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")
    )
    builder.adjust(1)
    return builder.as_markup()

# Кнопки подтверждения/отклонения
def get_admin_decision_keyboard(user_id: int, request_type: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_approve_{request_type}_{user_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_deny_{request_type}_{user_id}"),
        InlineKeyboardButton(text="📋 Назад к списку", callback_data=f"admin_{request_type}_list")
    )
    return builder.as_markup()