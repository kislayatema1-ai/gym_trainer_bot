from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import check_user_access, add_nutrition_report, get_nutrition_reports, save_calorie_norms, get_calorie_norms, add_calorie_request, get_pending_calorie_requests, update_calorie_request_status
from utils.bot_instance import bot
import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Состояния для отчетов о питании
class NutritionReport(StatesGroup):
    waiting_for_breakfast = State()
    waiting_for_lunch = State()
    waiting_for_dinner = State()
    waiting_for_snacks = State()
    waiting_for_water = State()
    waiting_for_notes = State()

# Состояния для расчета калорий
class CalorieCalculation(StatesGroup):
    waiting_for_age = State()
    waiting_for_weight = State()
    waiting_for_height = State()
    waiting_for_gender = State()
    waiting_for_activity = State()
    waiting_for_goal = State()

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
    builder.button(text="Мужской", callback_data="gender_male")
    builder.button(text="Женский", callback_data="gender_female")
    return builder.as_markup()

def get_activity_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Сидячий образ жизни", callback_data="activity_sedentary")
    builder.button(text="Легкая активность", callback_data="activity_light")
    builder.button(text="Умеренная активность", callback_data="activity_moderate")
    builder.button(text="Высокая активность", callback_data="activity_high")
    builder.button(text="Экстремальная активность", callback_data="activity_extreme")
    builder.adjust(1)
    return builder.as_markup()

def get_goal_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Похудение", callback_data="goal_lose")
    builder.button(text="Поддержание веса", callback_data="goal_maintain")
    builder.button(text="Набор массы", callback_data="goal_gain")
    builder.adjust(1)
    return builder.as_markup()

# Расчет калорий
@router.callback_query(F.data == "nutrition_calories_calc")
async def start_calorie_calculation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔢 Введите ваш возраст:")
    await state.set_state(CalorieCalculation.waiting_for_age)
    await callback.answer()

@router.message(CalorieCalculation.waiting_for_age, F.text)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if 10 <= age <= 100:
            await state.update_data(age=age)
            await message.answer("⚖️ Введите ваш вес (в кг):")
            await state.set_state(CalorieCalculation.waiting_for_weight)
        else:
            await message.answer("Пожалуйста, введите корректный возраст (10-100 лет):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.message(CalorieCalculation.waiting_for_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if 30 <= weight <= 200:
            await state.update_data(weight=weight)
            await message.answer("📏 Введите ваш рост (в см):")
            await state.set_state(CalorieCalculation.waiting_for_height)
        else:
            await message.answer("Пожалуйста, введите корректный вес (30-200 кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.message(CalorieCalculation.waiting_for_height, F.text)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if 100 <= height <= 250:
            await state.update_data(height=height)
            await message.answer("👤 Выберите пол:", reply_markup=get_gender_keyboard())
        else:
            await message.answer("Пожалуйста, введите корректный рост (100-250 см):")
    except ValueError:
        await message.answer("Пожалуйста, введите число:")

@router.callback_query(F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = "male" if callback.data == "gender_male" else "female"
    await state.update_data(gender=gender)
    await callback.message.edit_text("🏃‍♂️ Выберите уровень активности:", reply_markup=get_activity_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("activity_"))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    activity_map = {
        "activity_sedentary": "sedentary",
        "activity_light": "light",
        "activity_moderate": "moderate",
        "activity_high": "high",
        "activity_extreme": "extreme"
    }
    await state.update_data(activity=activity_map[callback.data])
    await callback.message.edit_text("🎯 Выберите цель:", reply_markup=get_goal_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal_map = {
        "goal_lose": "lose",
        "goal_maintain": "maintain",
        "goal_gain": "gain"
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
    text = (
        "📚 Книга рецептов:\n\n"
        "Скоро здесь появятся полезные и вкусные рецепты для вашего рациона!\n\n"
        "А пока вы можете:\n"
        "• Использовать чек-лист продуктов для составления меню\n"
        "• Спросить тренера о рецептах в разделе связи\n"
        "• Следить за нашими обновлениями"
    )
    await callback.message.answer(text)
    await callback.answer()