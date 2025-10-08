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
        InlineKeyboardButton(text="📚 Книга рецептов", callback_data="nutrition_recipes_main"),
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
def get_admin_payment_decision_kb(user_id: int, product_type: str = 'full'):
    """Клавиатура для админа"""
    builder = InlineKeyboardBuilder()
    
    # Всегда передаем только user_id и product_type, без дней
    builder.button(text="✅ Одобрить", callback_data=f"approve_{user_id}_{product_type}")
    builder.button(text="❌ Отклонить", callback_data=f"deny_{user_id}_{product_type}")
    builder.adjust(2)
    return builder.as_markup()

# --- Главное меню тренировок (С кнопкой Назад) ---
def get_training_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🆕 Создать таблицу", callback_data="training_create_sheet"),
        InlineKeyboardButton(text="📊 Моя таблица", callback_data="training_my_sheet"),
        InlineKeyboardButton(text="📈 Мой прогресс", callback_data="training_progress"),
        InlineKeyboardButton(text="ℹ️ Инструкция", callback_data="training_help"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")  # ДОБАВИЛ кнопку Назад
    )
    builder.adjust(2)  # По 2 кнопки в ряду
    return builder.as_markup()

# --- Клавиатура для внутренних разделов (с кнопкой Назад) ---
def get_training_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="◀️ Назад в меню тренировок", callback_data="training_back_to_main")
    )
    return builder.as_markup()

# --- Reply клавиатура для раздела тренировок ---
def get_training_reply_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🆕 Создать таблицу"),
        KeyboardButton(text="📊 Моя таблица"),
        KeyboardButton(text="📝 Инструкция"),
        KeyboardButton(text="⬅️ Назад в меню")
    )
    builder.adjust(2)  # По 2 кнопки в ряду
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# --- Клавиатуры для книги рецептов ---

def get_recipes_main_keyboard():
    """Главное меню книги рецептов"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🍳 По категориям", callback_data="recipes_by_category")
    builder.button(text="⚡ По времени готовки", callback_data="recipes_by_time")
    builder.button(text="🔥 По калориям", callback_data="recipes_by_calories")
    builder.button(text="🔍 Поиск рецепта", callback_data="recipes_search")
    builder.button(text="⭐ Избранное", callback_data="recipes_favorites")
    builder.button(text="🎲 Случайный рецепт", callback_data="recipes_random")
    builder.button(text="◀️ Назад", callback_data="nutrition_back")
    builder.adjust(2)
    return builder.as_markup()

def get_recipes_categories_keyboard():
    """Категории рецептов"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🥗 Завтраки", callback_data="recipes_category_breakfast")
    builder.button(text="🍲 Обеды", callback_data="recipes_category_lunch")
    builder.button(text="🍽️ Ужины", callback_data="recipes_category_dinner")
    builder.button(text="🍎 Перекусы", callback_data="recipes_category_snacks")
    builder.button(text="🥤 Смузи и напитки", callback_data="recipes_category_drinks")
    builder.button(text="🍰 Десерты", callback_data="recipes_category_desserts")
    builder.button(text="🍗 Белковые блюда", callback_data="recipes_category_protein")
    builder.button(text="🥦 Вегетарианские", callback_data="recipes_category_vegetarian")
    builder.button(text="◀️ Назад", callback_data="recipes_main")
    builder.adjust(2)
    return builder.as_markup()

def get_recipes_time_keyboard():
    """Фильтр по времени готовки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ До 15 мин", callback_data="recipes_time_15")
    builder.button(text="🕒 15-30 мин", callback_data="recipes_time_30")
    builder.button(text="⏰ 30-60 мин", callback_data="recipes_time_60")
    builder.button(text="🍳 Более 60 мин", callback_data="recipes_time_60plus")
    builder.button(text="◀️ Назад", callback_data="recipes_main")
    builder.adjust(2)
    return builder.as_markup()

def get_recipes_calories_keyboard():
    """Фильтр по калориям"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🥬 До 200 ккал", callback_data="recipes_calories_200")
    builder.button(text="🍎 200-400 ккал", callback_data="recipes_calories_400")
    builder.button(text="🥩 400-600 ккал", callback_data="recipes_calories_600")
    builder.button(text="🍛 Более 600 ккал", callback_data="recipes_calories_600plus")
    builder.button(text="◀️ Назад", callback_data="recipes_main")
    builder.adjust(2)
    return builder.as_markup()

def get_recipe_navigation_keyboard(recipe_id, total_recipes, category=None, is_favorite=False):
    """Навигация по рецептам с кнопкой избранного"""
    builder = InlineKeyboardBuilder()
    
    if recipe_id > 1:
        builder.button(text="⬅️ Предыдущий", callback_data=f"recipe_prev_{recipe_id-1}_{category}")
    
    # Динамическая кнопка избранного
    favorite_text = "❌ Удалить из избранного" if is_favorite else "⭐ В избранное"
    favorite_data = f"recipe_unfavorite_{recipe_id}_{category}" if is_favorite else f"recipe_favorite_{recipe_id}_{category}"
    builder.button(text=favorite_text, callback_data=favorite_data)
    
    if recipe_id < total_recipes:
        builder.button(text="Следующий ➡️", callback_data=f"recipe_next_{recipe_id+1}_{category}")
    
    builder.button(text="📋 Список рецептов", callback_data=f"recipes_category_{category}")
    builder.button(text="◀️ Назад", callback_data="recipes_by_category")
    builder.adjust(2)
    return builder.as_markup()