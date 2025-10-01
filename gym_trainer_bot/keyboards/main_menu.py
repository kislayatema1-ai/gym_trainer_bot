from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- Главное меню (Reply клавиатура) ---
def get_main_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🏋️ Тренировки"),
        KeyboardButton(text="🥗 Питание"),
        KeyboardButton(text="📚 Упражнения"),
        KeyboardButton(text="📊 Прогресс"),
        KeyboardButton(text="💳 Оплата / Доступ"),
        KeyboardButton(text="📞 Связь с тренером"),
        KeyboardButton(text="❓ FAQ")
    )
    builder.adjust(2)  # Размещаем кнопки по 2 в ряду
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# --- Клавиатура для раздела "Оплата / Доступ" ---
def get_payment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="💳 Оплатить абонемент", callback_data="pay_subscription"),
        InlineKeyboardButton(text="ℹ️ Инструкция по оплате", callback_data="pay_instructions"),
        InlineKeyboardButton(text="✅ Проверить мой доступ", callback_data="check_my_access"),
        InlineKeyboardButton(text="📞 Связь по оплате", callback_data="support_contact"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

# Кнопка "Я оплатил(а)" для отправки скриншота
def get_paid_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data="i_paid"))
    return builder.as_markup()

# Клавиатура для раздела Прогресс
def get_progress_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📈 Добавить вес", callback_data="progress_add_weight"),
        InlineKeyboardButton(text="📏 Добавить замеры", callback_data="progress_add_measurements"),
        InlineKeyboardButton(text="🏆 Мои достижения", callback_data="progress_achievements"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="progress_stats"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для раздела "Питание"
def get_nutrition_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🎯 Твоя норма калорий", callback_data="nutrition_calories_norm"),
        InlineKeyboardButton(text="🧮 Расчет калорий", callback_data="nutrition_calories_calc"),
        InlineKeyboardButton(text="💡 Рекомендации", callback_data="nutrition_recom"),
        InlineKeyboardButton(text="🛒 Чек-лист продуктов", callback_data="nutrition_checklist"),
        InlineKeyboardButton(text="📚 Книга рецептов", callback_data="nutrition_recipes"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для раздела FAQ
def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq_main"),
        InlineKeyboardButton(text="📞 Связь с тренером", callback_data="support_contact"),
        InlineKeyboardButton(text="🎥 Как снимать упражнения", callback_data="faq_video_guide"),
        InlineKeyboardButton(text="📊 Как вести отчеты", callback_data="faq_reports_guide"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура категорий FAQ (исправляем кнопку Назад)
def get_faq_categories_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        category_id, category_name, description = category
        builder.button(text=category_name, callback_data=f"faq_cat_{category_id}")
    builder.button(text="📞 Связь с тренером", callback_data="support_contact")
    builder.button(text="◀️ Назад", callback_data="faq_back_to_main")  # Изменяем callback
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для раздела "Упражнения"
def get_exercises_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🎥 Видеоуроки", callback_data="exercises_videos"),
        InlineKeyboardButton(text="📚 Советы и литература", callback_data="exercises_literature"),
        InlineKeyboardButton(text="🧤 Работа с инвентарем", callback_data="exercises_equipment"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()

# Кнопки для админа (Подтвердить/Отклонить платеж)
def get_admin_payment_decision_kb(user_id, product_type='full'):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"approve_{user_id}_{product_type}")
    builder.button(text="❌ Отклонить", callback_data=f"deny_{user_id}_{product_type}")
    builder.adjust(2)
    return builder.as_markup()

# --- Клавиатура для раздела "Тренировки" ---
def get_training_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="📊 Моя таблица тренировок", callback_data="training_my_sheet"),
        InlineKeyboardButton(text="💪 Начать тренировку", callback_data="training_start"),
        InlineKeyboardButton(text="📈 Мой прогресс", callback_data="training_progress"),
        InlineKeyboardButton(text="ℹ️ Инструкция", callback_data="training_help"),
        InlineKeyboardButton(text="🆕 Создать таблицу", callback_data="training_create_sheet"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    builder.adjust(1)
    return builder.as_markup()