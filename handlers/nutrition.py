from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import check_user_access, add_nutrition_report, get_nutrition_reports, save_calorie_norms, get_calorie_norms, add_calorie_request, get_pending_calorie_requests, update_calorie_request_status
# Добавьте эти импорты после других импортов из database
from database import add_favorite_recipe, remove_favorite_recipe, get_favorite_recipes, is_recipe_favorite
from utils.bot_instance import bot
import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from data.recipes_database import RECIPES_DATABASE

router = Router()

# Состояния для отчетов о питании
class NutritionReport(StatesGroup):
    waiting_for_breakfast = State()
    waiting_for_lunch = State()
    waiting_for_dinner = State()
    waiting_for_snacks = State()
    waiting_for_water = State()
    waiting_for_notes = State()

# Состояния для расчета калорий (переименованы чтобы не конфликтовать с onboarding)
class NutritionCalorieCalculation(StatesGroup):
    waiting_for_calorie_age = State()
    waiting_for_calorie_weight = State()
    waiting_for_calorie_height = State()
    waiting_for_calorie_gender = State()
    waiting_for_calorie_activity = State()
    waiting_for_calorie_goal = State()

# Добавьте состояние для поиска рецептов
class RecipeSearch(StatesGroup):
    waiting_for_search_term = State()

# Отчет о питании
@router.callback_query(F.data == "nutrition_report")
async def start_nutrition_report(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🍳 Расскажите о своем завтраке:")
    await state.set_state(NutritionReport.waiting_for_breakfast)
    await callback.answer()

@router.message(NutritionReport.waiting_for_breakfast, F.text)
async def process_breakfast(message: Message, state: FSMContext):
    await state.update_data(breakfast=message.text)
    await message.answer("🍲 Теперь опишите обед:")
    await state.set_state(NutritionReport.waiting_for_lunch)

@router.message(NutritionReport.waiting_for_lunch, F.text)
async def process_lunch(message: Message, state: FSMContext):
    await state.update_data(lunch=message.text)
    await message.answer("🍽️ Теперь опишите ужин:")
    await state.set_state(NutritionReport.waiting_for_dinner)

@router.message(NutritionReport.waiting_for_dinner, F.text)
async def process_dinner(message: Message, state: FSMContext):
    await state.update_data(dinner=message.text)
    await message.answer("🍎 Были перекусы? Опишите:")
    await state.set_state(NutritionReport.waiting_for_snacks)

@router.message(NutritionReport.waiting_for_snacks, F.text)
async def process_snacks(message: Message, state: FSMContext):
    await state.update_data(snacks=message.text)
    await message.answer("💧 Сколько воды выпили (в литрах)?")
    await state.set_state(NutritionReport.waiting_for_water)

@router.message(NutritionReport.waiting_for_water, F.text)
async def process_water(message: Message, state: FSMContext):
    try:
        water = float(message.text)
        await state.update_data(water=water)
        await message.answer("📝 Дополнительные заметки по питанию (или напишите 'нет'):")
        await state.set_state(NutritionReport.waiting_for_notes)
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 1.5 или 2):")

@router.message(NutritionReport.waiting_for_notes, F.text)
async def process_notes(message: Message, state: FSMContext):
    data = await state.get_data()
    notes = message.text if message.text.lower() != 'нет' else ''
    
    # Сохраняем отчет
    await add_nutrition_report(
        message.from_user.id,
        data['breakfast'],
        data['lunch'],
        data['dinner'],
        data['snacks'],
        data['water'],
        notes
    )
    
    await message.answer("✅ Отчет о питании сохранен! Отличная работа над отслеживанием рациона!")
    await state.clear()

# Норма калорий
@router.callback_query(F.data == "nutrition_calories_norm")
async def show_calorie_norms(callback: CallbackQuery):
    norms = await get_calorie_norms(callback.from_user.id)
    if norms:
        calories, protein, fat, carbs, updated = norms
        text = (
            f"📊 Ваши дневные нормы:\n\n"
            f"• Калории: {calories} ккал\n"
            f"• Белки: {protein} г\n"
            f"• Жиры: {fat} г\n"
            f"• Углеводы: {carbs} г\n\n"
            f"Обновлено: {datetime.datetime.fromisoformat(updated).strftime('%d.%m.%Y')}"
        )
    else:
        text = "У вас еще не рассчитаны нормы питания. Используйте «Расчет калорий» для получения индивидуальных рекомендаций."
    
    await callback.message.answer(text)
    await callback.answer()

# Вспомогательные функции для клавиатур
def get_gender_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Мужской", callback_data="nutrition_gender_male")
    builder.button(text="Женский", callback_data="nutrition_gender_female")
    return builder.as_markup()

def get_activity_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Сидячий образ жизни", callback_data="nutrition_activity_sedentary")
    builder.button(text="Легкая активность", callback_data="nutrition_activity_light")
    builder.button(text="Умеренная активность", callback_data="nutrition_activity_moderate")
    builder.button(text="Высокая активность", callback_data="nutrition_activity_high")
    builder.button(text="Экстремальная активность", callback_data="nutrition_activity_extreme")
    builder.adjust(1)
    return builder.as_markup()

def get_goal_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Похудение", callback_data="nutrition_goal_lose")
    builder.button(text="Поддержание веса", callback_data="nutrition_goal_maintain")
    builder.button(text="Набор массы", callback_data="nutrition_goal_gain")
    builder.adjust(1)
    return builder.as_markup()

# Расчет калорий
@router.callback_query(F.data == "nutrition_calories_calc")
async def start_calorie_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔢 Введите ваш возраст:")
    await state.set_state(NutritionCalorieCalculation.waiting_for_calorie_age)
    await callback.answer()

@router.message(NutritionCalorieCalculation.waiting_for_calorie_age, F.text)
async def process_calorie_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if 10 <= age <= 100:
            await state.update_data(age=age)
            await message.answer("⚖️ Введите ваш вес (в кг):")
            await state.set_state(NutritionCalorieCalculation.waiting_for_calorie_weight)
        else:
            await message.answer("Пожалуйста, введите корректный возраст (10-100 лет):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.message(NutritionCalorieCalculation.waiting_for_calorie_weight, F.text)
async def process_calorie_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if 30 <= weight <= 200:
            await state.update_data(weight=weight)
            await message.answer("📏 Введите ваш рост (в см):")
            await state.set_state(NutritionCalorieCalculation.waiting_for_calorie_height)
        else:
            await message.answer("Пожалуйста, введите корректный вес (30-200 кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.message(NutritionCalorieCalculation.waiting_for_calorie_height, F.text)
async def process_calorie_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if 100 <= height <= 250:
            await state.update_data(height=height)
            await message.answer("👤 Выберите пол:", reply_markup=get_gender_keyboard())
        else:
            await message.answer("Пожалуйста, введите корректный рост (100-250 см):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.callback_query(F.data.startswith("nutrition_gender_"))
async def process_calorie_gender(callback: CallbackQuery, state: FSMContext):
    gender = "male" if callback.data == "nutrition_gender_male" else "female"
    await state.update_data(gender=gender)
    await callback.message.edit_text("🏃‍♂️ Выберите уровень активности:", reply_markup=get_activity_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("nutrition_activity_"))
async def process_calorie_activity(callback: CallbackQuery, state: FSMContext):
    activity_map = {
        "nutrition_activity_sedentary": "sedentary",
        "nutrition_activity_light": "light", 
        "nutrition_activity_moderate": "moderate",
        "nutrition_activity_high": "high",
        "nutrition_activity_extreme": "extreme"
    }
    await state.update_data(activity=activity_map[callback.data])
    await callback.message.edit_text("🎯 Выберите цель:", reply_markup=get_goal_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("nutrition_goal_"))
async def process_calorie_goal(callback: CallbackQuery, state: FSMContext):
    goal_map = {
        "nutrition_goal_lose": "lose",
        "nutrition_goal_maintain": "maintain",
        "nutrition_goal_gain": "gain"
    }
    data = await state.get_data()
    data['goal'] = goal_map[callback.data]
    
    # Сохраняем запрос
    await add_calorie_request(
        callback.from_user.id,
        data['age'],
        data['weight'],
        data['height'],
        data['gender'],
        data['activity'],
        data['goal']
    )
    
    await callback.message.edit_text(
        "✅ Ваши данные отправлены тренеру для расчета индивидуальных норм! "
        "Обычно расчет занимает до 24 часов. Вы получите уведомление, когда нормы будут готовы."
    )
    await state.clear()
    
    # Уведомляем админа
    admin_text = (
        f"📋 Новый запрос на расчет калорий от {callback.from_user.full_name}\n\n"
        f"• Возраст: {data['age']}\n"
        f"• Вес: {data['weight']} кг\n"
        f"• Рост: {data['height']} см\n"
        f"• Пол: {'Мужской' if data['gender'] == 'male' else 'Женский'}\n"
        f"• Активность: {data['activity']}\n"
        f"• Цель: {data['goal']}\n\n"
        f"👤 @{callback.from_user.username}"
    )
    await bot.send_message(chat_id=config.ADMIN_ID, text=admin_text)

# Команды для админа (управление расчетом калорий)
@router.message(Command("calorierequests"))
async def cmd_calorie_requests(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    requests = await get_pending_calorie_requests()
    if not requests:
        await message.answer("Нет запросов на расчет калорий.")
        return
    
    text = "📋 Запросы на расчет калорий:\n\n"
    for req in requests:
        request_id, user_id, full_name, username, age, weight, height, gender, activity, goal, created = req
        text += f"👤 {full_name} (@{username})\n"
        text += f"📊 Возраст: {age}, Вес: {weight}кг, Рост: {height}см\n"
        text += f"🎯 Цель: {goal}, Активность: {activity}\n"
        text += f"🆔 ID запроса: {request_id}\n"
        text += "─" * 30 + "\n"
    
    await message.answer(text)

@router.message(Command("setcalories"))
async def cmd_set_calories(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    try:
        # Команда: /setcalories <user_id> <calories> <protein> <fat> <carbs>
        parts = message.text.split()
        if len(parts) != 6:
            await message.answer("Использование: /setcalories <user_id> <calories> <protein> <fat> <carbs>")
            return
        
        user_id = int(parts[1])
        calories = int(parts[2])
        protein = int(parts[3])
        fat = int(parts[4])
        carbs = int(parts[5])
        
        await save_calorie_norms(user_id, calories, protein, fat, carbs)
        
        # Обновляем статус всех pending запросов этого пользователя
        await update_calorie_request_status(user_id, 'approved')
        
        await message.answer(f"✅ Нормы для пользователя {user_id} установлены!")
        
        # Уведомляем пользователя
        user_text = (
            f"🎉 Ваши индивидуальные нормы питания готовы!\n\n"
            f"• Калории: {calories} ккал/день\n"
            f"• Белки: {protein} г/день\n"
            f"• Жиры: {fat} г/день\n"
            f"• Углеводы: {carbs} г/день\n\n"
            f"Проверить нормы можно в разделе «🥗 Питание» → «Твоя норма калорий»"
        )
        await bot.send_message(chat_id=user_id, text=user_text)
        
    except (ValueError, IndexError):
        await message.answer("Ошибка в формате команды. Использование: /setcalories <user_id> <calories> <protein> <fat> <carbs>")

# Заглушки для остальных пунктов
@router.callback_query(F.data == "nutrition_recom")
async def nutrition_recom(callback: CallbackQuery):
    text = (
        "🍎 Общие рекомендации по питанию:\n\n"
        "• Ешьте разнообразную пищу\n"
        "• Пейте 2-3 литра воды в день\n"
        "• Употребляйте белок с каждым приемом пищи\n"
        "• Ограничьте processed food\n"
        "• Ешьте овощи и фрукты ежедневно\n\n"
        "Для индивидуальных рекомендаций свяжитесь с тренером."
    )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "nutrition_checklist")
async def nutrition_checklist(callback: CallbackQuery):
    text = (
        "🛒 Чек-лист полезных продуктов:\n\n"
        "✅ Белки:\n• Куриная грудка\n• Говядина\n• Рыба\n• Яйца\n• Творог\n• Тофу\n\n"
        "✅ Углеводы:\n• Гречка\n• Рис\n• Овсянка\n• Киноа\n• Батат\n• Цельнозерновой хлеб\n\n"
        "✅ Жиры:\n• Авокадо\n• Орехи\n• Оливковое масло\n• Жирная рыба\n• Семена\n\n"
        "✅ Овощи:\n• Брокколи\n• Шпинат\n• Морковь\n• Помидоры\n• Огурцы\n• Цветная капуста"
    )
    await callback.message.answer(text)
    await callback.answer()

@router.callback_query(F.data == "nutrition_recipes")
async def nutrition_recipes(callback: CallbackQuery):
    from keyboards.main_menu import get_recipes_main_keyboard
    text = (
        "📚 *КНИГА РЕЦЕПТОВ*\n\n"
        "Выберите способ поиска рецептов:"
    )
    await callback.message.edit_text(text, reply_markup=get_recipes_main_keyboard())
    await callback.answer()

# --- КНИГА РЕЦЕПТОВ ---

@router.callback_query(F.data == "nutrition_recipes_main")
async def nutrition_recipes_main(callback: CallbackQuery):
    from keyboards.main_menu import get_recipes_main_keyboard
    text = (
        "📚 *КНИГА РЕЦЕПТОВ*\n\n"
        "Выберите способ поиска рецептов:\n\n"
        "🍳 *По категориям* - завтраки, обеды, ужины\n"
        "⚡ *По времени* - быстрые рецепты\n"  
        "🔥 *По калориям* - для ваших целей\n"
        "🔍 *Поиск* - найти по названию\n"
        "⭐ *Избранное* - ваши любимые рецепты\n"
        "🎲 *Случайный* - рецепт дня!"
    )
    await callback.message.edit_text(text, reply_markup=get_recipes_main_keyboard())
    await callback.answer()

@router.callback_query(F.data == "recipes_by_category")
async def recipes_by_category(callback: CallbackQuery, state: FSMContext):
    from keyboards.main_menu import get_recipes_categories_keyboard
    text = (
        "🥗 *РЕЦЕПТЫ ПО КАТЕГОРИЯМ*\n\n"
        "Выберите категорию:"
    )
    await state.clear()  # Очищаем состояние поиска
    await callback.message.edit_text(text, reply_markup=get_recipes_categories_keyboard())
    await callback.answer()

@router.callback_query(F.data == "recipes_by_time")
async def recipes_by_time(callback: CallbackQuery, state: FSMContext):
    from keyboards.main_menu import get_recipes_time_keyboard
    text = (
        "⚡ *РЕЦЕПТЫ ПО ВРЕМЕНИ*\n\n"
        "Выберите время готовки:"
    )
    await state.clear()  # Очищаем состояние
    await callback.message.edit_text(text, reply_markup=get_recipes_time_keyboard())
    await callback.answer()

@router.callback_query(F.data == "recipes_by_calories")
async def recipes_by_calories(callback: CallbackQuery, state: FSMContext):
    from keyboards.main_menu import get_recipes_calories_keyboard
    text = (
        "🔥 *РЕЦЕПТЫ ПО КАЛОРИЯМ*\n\n"
        "Выберите калорийность:"
    )
    await state.clear()  # Очищаем состояние
    await callback.message.edit_text(text, reply_markup=get_recipes_calories_keyboard())
    await callback.answer()

@router.callback_query(F.data == "recipes_search")
async def recipes_search(callback: CallbackQuery, state: FSMContext):
    text = (
        "🔍 *ПОИСК РЕЦЕПТА*\n\n"
        "Введите название ингредиента или блюда:\n\n"
        "Например: *курица*, *овсянка*, *шпинат*"
    )
    await callback.message.answer(text)
    await state.set_state(RecipeSearch.waiting_for_search_term)
    await callback.answer()

# Обработчики избранного с БД
@router.callback_query(F.data.startswith("recipe_favorite_"))
async def add_to_favorites(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    recipe_id = int(parts[2])
    category = parts[3]
    
    success = await add_favorite_recipe(user_id, category, recipe_id)
    if success:
        await callback.answer("✅ Рецепт добавлен в избранное!")
        # Обновляем клавиатуру
        await update_recipe_keyboard(callback, recipe_id, category, True)
    else:
        await callback.answer("❌ Ошибка при добавлении в избранное")

@router.callback_query(F.data.startswith("recipe_unfavorite_"))
async def remove_from_favorites(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    recipe_id = int(parts[2])
    category = parts[3]
    
    await remove_favorite_recipe(user_id, category, recipe_id)
    await callback.answer("❌ Рецепт удален из избранного")
    # Обновляем клавиатуру
    await update_recipe_keyboard(callback, recipe_id, category, False)

async def update_recipe_keyboard(callback, recipe_id, category, is_favorite):
    """Обновляет клавиатуру рецепта после изменения избранного"""
    from keyboards.main_menu import get_recipe_navigation_keyboard
    
    if category in RECIPES_DATABASE:
        recipes = RECIPES_DATABASE[category]
        current_recipe = None
        current_num = 0
        
        for i, recipe in enumerate(recipes, 1):
            if recipe['id'] == recipe_id:
                current_recipe = recipe
                current_num = i
                break
        
        if current_recipe:
            await callback.message.edit_reply_markup(
                reply_markup=get_recipe_navigation_keyboard(
                    current_num, len(recipes), category, is_favorite
                )
            )

@router.callback_query(F.data == "recipes_favorites")
async def recipes_favorites(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    favorites = await get_favorite_recipes(user_id)
    
    if not favorites:
        text = (
            "⭐ *ИЗБРАННЫЕ РЕЦЕПТЫ*\n\n"
            "У вас пока нет избранных рецептов.\n\n"
            "Чтобы добавить рецепт в избранное, нажмите ⭐ на любом рецепте."
        )
        await state.clear()  # Очищаем состояние
        await callback.message.answer(text)
    else:
        from keyboards.main_menu import InlineKeyboardBuilder, InlineKeyboardButton
        
        builder = InlineKeyboardBuilder()
        text = "⭐ *ВАШИ ИЗБРАННЫЕ РЕЦЕПТЫ:*\n\n"
        
        # Группируем рецепты по категориям для красивого отображения
        categorized_recipes = {}
        
        for category, recipe_id in favorites:
            if category not in categorized_recipes:
                categorized_recipes[category] = []
            
            # Находим рецепт в базе
            if category in RECIPES_DATABASE:
                for recipe in RECIPES_DATABASE[category]:
                    if recipe['id'] == recipe_id:
                        categorized_recipes[category].append(recipe)
                        break
        
        # Отображаем рецепты по категориям
        for category, recipes in categorized_recipes.items():
            category_name = {
                "breakfast": "🥗 Завтраки",
                "lunch": "🍲 Обеды", 
                "dinner": "🍽️ Ужины",
                "snacks": "🍎 Перекусы",
                "drinks": "🥤 Напитки",
                "desserts": "🍰 Десерты",
                "protein": "🍗 Белковые",
                "vegetarian": "🥦 Вегетарианские"
            }.get(category, category)
            
            text += f"*{category_name}:*\n"
            for recipe in recipes:
                text += f"• {recipe['name']} ({recipe['calories']} ккал)\n"
                builder.button(
                    text=f"👁️ {recipe['name'][:15]}...", 
                    callback_data=f"fav_view_{category}_{recipe['id']}"
                )
            text += "\n"
        
        builder.button(text="◀️ Назад", callback_data="recipes_main")
        builder.adjust(2)
        
        await state.clear()  # Очищаем состояние
        await callback.message.answer(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("fav_view_"))
async def view_favorite_recipe(callback: CallbackQuery):
    parts = callback.data.split("_")
    category = parts[2]
    recipe_id = int(parts[3])
    
    if category in RECIPES_DATABASE:
        recipes = RECIPES_DATABASE[category]
        for i, recipe in enumerate(recipes, 1):
            if recipe['id'] == recipe_id:
                # Проверяем, есть ли рецепт в избранном
                is_favorite = await is_recipe_favorite(callback.from_user.id, category, recipe_id)
                await show_recipe(callback, recipe, category, i, len(recipes), is_favorite)
                break
    await callback.answer()

@router.callback_query(F.data == "recipes_random")
async def recipes_random(callback: CallbackQuery):
    import random
    # Выбираем случайную категорию и рецепт
    categories = list(RECIPES_DATABASE.keys())
    random_category = random.choice(categories)
    recipes = RECIPES_DATABASE[random_category]
    random_recipe = random.choice(recipes)
    
    await show_recipe(callback, random_recipe, random_category, 1, len(recipes))
    await callback.answer()

@router.callback_query(F.data.startswith("recipes_category_"))
async def show_category_recipes(callback: CallbackQuery, state: FSMContext):
    category_map = {
        "recipes_category_breakfast": "breakfast",
        "recipes_category_lunch": "lunch", 
        "recipes_category_dinner": "dinner",
        "recipes_category_snacks": "snacks",
        "recipes_category_drinks": "drinks",
        "recipes_category_desserts": "desserts",
        "recipes_category_protein": "protein",
        "recipes_category_vegetarian": "vegetarian"
    }
    
    category = category_map.get(callback.data)
    if category in RECIPES_DATABASE and RECIPES_DATABASE[category]:
        recipes = RECIPES_DATABASE[category]
        await state.clear()  # Очищаем состояние
        await show_recipe(callback, recipes[0], category, 1, len(recipes))
    else:
        await callback.message.answer("🥺 В этой категории пока нет рецептов. Скоро добавим!")
    await callback.answer()

@router.callback_query(F.data.startswith("recipe_"))
async def navigate_recipes(callback: CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1]  # prev, next
    recipe_id = int(parts[2])
    category = parts[3] if len(parts) > 3 else None
    
    if category and category in RECIPES_DATABASE:
        recipes = RECIPES_DATABASE[category]
        if action == "prev" and recipe_id > 0:
            await show_recipe(callback, recipes[recipe_id-1], category, recipe_id, len(recipes))
        elif action == "next" and recipe_id <= len(recipes):
            await show_recipe(callback, recipes[recipe_id-1], category, recipe_id, len(recipes))
    
    await callback.answer()

async def show_recipe(callback, recipe, category, current_num, total_recipes, is_favorite=None):
    from keyboards.main_menu import get_recipe_navigation_keyboard
    
    # Если статус избранного не передан, проверяем в БД
    if is_favorite is None:
        is_favorite = await is_recipe_favorite(callback.from_user.id, category, recipe['id'])
    
    text = (
        f"{recipe['name']}\n\n"
        f"📊 *Пищевая ценность на порцию:*\n"
        f"• Калории: {recipe['calories']} ккал\n"
        f"• Белки: {recipe['protein']} г\n"
        f"• Углеводы: {recipe['carbs']} г\n"
        f"• Жиры: {recipe['fat']} г\n"
        f"⏱ Время готовки: {recipe['time']} мин\n\n"
        f"🛒 *Ингредиенты:*\n" + "\n".join(recipe['ingredients']) + "\n\n"
        f"👨‍🍳 *Приготовление:*\n" + "\n".join(recipe['instructions']) + "\n\n"
        f"💡 *Совет:* {recipe['tips']}\n\n"
        f"📖 Рецепт {current_num} из {total_recipes}"
    )
    
    await callback.message.edit_text(
        text, 
        reply_markup=get_recipe_navigation_keyboard(
            current_num, total_recipes, category, is_favorite
        )
    )

@router.callback_query(F.data == "nutrition_back")
async def nutrition_back(callback: CallbackQuery, state: FSMContext):
    from keyboards.main_menu import get_nutrition_keyboard
    await state.clear()  # Очищаем все состояния питания
    await callback.message.edit_text(
        "🥗 *Питание*\n\n"
        "Выберите раздел:",
        reply_markup=get_nutrition_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "recipes_main")
async def recipes_main_back(callback: CallbackQuery, state: FSMContext):
    """Назад в главное меню рецептов"""
    from keyboards.main_menu import get_recipes_main_keyboard
    text = (
        "📚 *КНИГА РЕЦЕПТОВ*\n\n"
        "Выберите способ поиска рецептов:"
    )
    await state.clear()  # Очищаем состояние поиска
    await callback.message.edit_text(text, reply_markup=get_recipes_main_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("recipes_time_"))
async def recipes_by_time_filter(callback: CallbackQuery):
    time_map = {
        "recipes_time_15": "до 15 минут",
        "recipes_time_30": "15-30 минут", 
        "recipes_time_60": "30-60 минут",
        "recipes_time_60plus": "более 60 минут"
    }
    
    time_filter = time_map.get(callback.data)
    if time_filter:
        # Показываем пример рецепта (позже добавим фильтрацию)
        import random
        categories = list(RECIPES_DATABASE.keys())
        random_category = random.choice(categories)
        recipes = RECIPES_DATABASE[random_category]
        
        # Ищем рецепт подходящий по времени
        suitable_recipes = [r for r in recipes if (
            (callback.data == "recipes_time_15" and r['time'] <= 15) or
            (callback.data == "recipes_time_30" and 15 < r['time'] <= 30) or
            (callback.data == "recipes_time_60" and 30 < r['time'] <= 60) or
            (callback.data == "recipes_time_60plus" and r['time'] > 60)
        )]
        
        if suitable_recipes:
            recipe = random.choice(suitable_recipes)
            await show_recipe(callback, recipe, random_category, 1, len(suitable_recipes))
        else:
            await callback.message.answer(f"🥺 Рецептов {time_filter} пока нет. Скоро добавим!")
    await callback.answer()

@router.callback_query(F.data.startswith("recipes_calories_"))
async def recipes_by_calories_filter(callback: CallbackQuery):
    calories_map = {
        "recipes_calories_200": "до 200 ккал",
        "recipes_calories_400": "200-400 ккал",
        "recipes_calories_600": "400-600 ккал", 
        "recipes_calories_600plus": "более 600 ккал"
    }
    
    calories_filter = calories_map.get(callback.data)
    if calories_filter:
        # Показываем пример рецепта (позже добавим фильтрацию)
        import random
        categories = list(RECIPES_DATABASE.keys())
        random_category = random.choice(categories)
        recipes = RECIPES_DATABASE[random_category]
        
        # Ищем рецепт подходящий по калориям
        suitable_recipes = [r for r in recipes if (
            (callback.data == "recipes_calories_200" and r['calories'] <= 200) or
            (callback.data == "recipes_calories_400" and 200 < r['calories'] <= 400) or
            (callback.data == "recipes_calories_600" and 400 < r['calories'] <= 600) or
            (callback.data == "recipes_calories_600plus" and r['calories'] > 600)
        )]
        
        if suitable_recipes:
            recipe = random.choice(suitable_recipes)
            await show_recipe(callback, recipe, random_category, 1, len(suitable_recipes))
        else:
            await callback.message.answer(f"🥺 Рецептов {calories_filter} пока нет. Скоро добавим!")
    await callback.answer()

# Обработчик поиска рецептов - ТОЛЬКО в состоянии поиска
@router.message(RecipeSearch.waiting_for_search_term, F.text & ~F.text.startswith('/'))
async def process_search(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    search_term = message.text.lower().strip()
    
    if len(search_term) < 3:
        await message.answer("🔍 Введите минимум 3 символа для поиска")
        return
    
    found_recipes = []
    
    # Ищем во всех категориях
    for category, recipes in RECIPES_DATABASE.items():
        for recipe in recipes:
            # Поиск по названию
            if search_term in recipe['name'].lower():
                found_recipes.append((recipe, category))
                continue
            
            # Поиск по ингредиентам
            ingredients_text = ' '.join(recipe['ingredients']).lower()
            if search_term in ingredients_text:
                found_recipes.append((recipe, category))
    
    if found_recipes:
        # Показываем первый найденный рецепт
        recipe, category = found_recipes[0]
        await show_recipe_search(message, recipe, category, 1, len(found_recipes), found_recipes)
        await state.clear()  # Очищаем состояние после успешного поиска
    else:
        await message.answer(
            f"🔍 По запросу \"{search_term}\" ничего не найдено.\n\n"
            "Попробуйте:\n"
            "• Другие ключевые слова\n" 
            "• Названия ингредиентов\n"
            "• Более общий запрос"
        )
        # Состояние остается активным для нового поиска

async def show_recipe_search(message, recipe, category, current_num, total_recipes, all_recipes):
    """Показ рецепта с навигацией для поиска"""
    from keyboards.main_menu import InlineKeyboardBuilder, InlineKeyboardButton
    
    builder = InlineKeyboardBuilder()
    
    if current_num > 1:
        prev_recipe, prev_category = all_recipes[current_num-2]
        builder.button(text="⬅️ Предыдущий", callback_data=f"search_prev_{current_num-1}")
    
    builder.button(text="⭐ В избранное", callback_data=f"recipe_favorite_{recipe['id']}_{category}")
    
    if current_num < total_recipes:
        next_recipe, next_category = all_recipes[current_num]
        builder.button(text="Следующий ➡️", callback_data=f"search_next_{current_num+1}")
    
    builder.button(text="🔍 Новый поиск", callback_data="recipes_search")
    builder.button(text="◀️ Назад", callback_data="recipes_main")
    builder.adjust(2)
    
    text = (
        f"🔍 *Найденный рецепт ({current_num} из {total_recipes}):*\n\n"
        f"{recipe['name']}\n\n"
        f"📊 *Пищевая ценность на порцию:*\n"
        f"• Калории: {recipe['calories']} ккал\n"
        f"• Белки: {recipe['protein']} г\n"
        f"• Углеводы: {recipe['carbs']} г\n"
        f"• Жиры: {recipe['fat']} г\n"
        f"⏱ Время готовки: {recipe['time']} мин\n\n"
        f"🛒 *Ингредиенты:*\n" + "\n".join(recipe['ingredients']) + "\n\n"
        f"👨‍🍳 *Приготовление:*\n" + "\n".join(recipe['instructions']) + "\n\n"
        f"💡 *Совет:* {recipe['tips']}"
    )
    
    await message.answer(text, reply_markup=builder.as_markup())

# Обработчики навигации для поиска
@router.callback_query(F.data.startswith("search_"))
async def navigate_search(callback: CallbackQuery):
    parts = callback.data.split("_")
    action = parts[1]  # prev, next
    position = int(parts[2])
    
    # Здесь нужно хранить результаты поиска, но для простоты сделаем повторный поиск
    # В реальном приложении нужно хранить результаты в состоянии или БД
    await callback.message.answer("🔍 Для просмотра других результатов выполните поиск заново")
    await callback.answer()