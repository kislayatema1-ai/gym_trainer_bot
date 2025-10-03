import asyncio
import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import update_onboarding_data, get_full_onboarding_data  # ИЗМЕНИЛИ НА get_full_onboarding_data
from utils.bot_instance import bot  # ДОБАВЛЯЕМ ИМПОРТ БОТА
from config import config
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Состояния для полной анкеты
class QuestionnaireState(StatesGroup):
    waiting_for_experience = State()
    waiting_for_equipment = State()
    waiting_for_schedule = State()
    waiting_for_food_preferences = State()
    waiting_for_health_issues = State()
    waiting_for_age_questionnaire = State()
    waiting_for_height_questionnaire = State()
    waiting_for_weight_questionnaire = State()
    waiting_for_activity_level = State()
    waiting_for_sleep = State()
    waiting_for_stress = State()
    waiting_for_gym_equipment = State()
    waiting_for_training_days = State()
    waiting_for_training_time = State()
    waiting_for_food_allergies = State()
    waiting_for_favorite_foods = State()
    waiting_for_disliked_foods = State()
    waiting_for_water_intake = State()
    waiting_for_supplements = State()
    waiting_for_injuries = State()
    waiting_for_goals = State()
    waiting_for_motivation = State()
    waiting_for_steps = State()

# Запуск полной анкеты после подтверждения оплаты
async def start_full_questionnaire(user_id: int):
    try:
        await bot.send_message(
            user_id,
            "🎉 *Добро пожаловать в команду!*\n\n"
            "Теперь я составлю для тебя персональную программу тренировок и питания.\n\n"
            "Ответь на несколько вопросов - это займет 5-10 минут. "
            "Чем подробнее ответишь, тем лучше будет программа! 💪"
        )
        
        # Начинаем с опыта тренировок
        from aiogram.fsm.context import FSMContext
        # Создаем временный state для пользователя
        # В реальной реализации нужно сохранять state для каждого пользователя
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🤷‍♀️ Нет опыта в зале", callback_data="exp_zero")
        builder.button(text="🚶 Начинающий (0-6 месяцев)", callback_data="exp_beginner")
        builder.button(text="🏃 Опытный (6+ месяцев)", callback_data="exp_intermediate") 
        builder.button(text="🏆 Продвинутый (2+ года)", callback_data="exp_advanced")
        builder.adjust(1)
        
        await bot.send_message(
            user_id,
            "1/10 • Какой у тебя опыт тренировок?",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        print(f"Error starting questionnaire: {e}")

# Обработка опыта тренировок
@router.callback_query(F.data.startswith("exp_"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    exp_map = {
        "exp_zero": "Нет опыта в зале",
        "exp_beginner": "Начинающий (1-6 месяцев)",
        "exp_intermediate": "Опытный (6+ месяцев)", 
        "exp_advanced": "Продвинутый (2+ года)"
    }
    
    experience = exp_map[callback.data]
    await update_onboarding_data(callback.from_user.id, experience=experience)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏋️ Тренажерный зал (полное оснащение)", callback_data="equip_full")
    builder.button(text="💪 Домашний спортзал (гантели, скамья)", callback_data="equip_home")
    builder.button(text="🏠 Минимум (резинки, коврик)", callback_data="equip_minimal")
    builder.button(text="🚴 Кардио-оборудование (беговая, велотренажер)", callback_data="equip_cardio")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"1. Опыт: {experience} ✅\n\n"
        "2/10 • Какое оборудование доступно для тренировок?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка оборудования
@router.callback_query(F.data.startswith("equip_"))
async def process_equipment(callback: CallbackQuery, state: FSMContext):
    equip_map = {
        "equip_full": "Тренажерный зал (полное оснащение)",
        "equip_home": "Домашний спортзал (гантели, скамья)",
        "equip_minimal": "Минимум (резинки, коврик)",
        "equip_cardio": "Кардио-оборудование (беговая, велотренажер)"
    }
    
    equipment = equip_map[callback.data]
    await update_onboarding_data(callback.from_user.id, equipment=equipment)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🌅 Утро (6-10 утра)", callback_data="time_morning")
    builder.button(text="🌇 День (10-16 дня)", callback_data="time_day")
    builder.button(text="🌆 Вечер (16-22 вечера)", callback_data="time_evening")
    builder.button(text="🕐 Свободный график", callback_data="time_flexible")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"2. Оборудование: {equipment} ✅\n\n"
        "3/10 • В какое время удобно тренироваться?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка времени тренировок
@router.callback_query(F.data.startswith("time_"))
async def process_schedule(callback: CallbackQuery, state: FSMContext):
    time_map = {
        "time_morning": "Утро (6-10 утра)",
        "time_day": "День (10-16 дня)",
        "time_evening": "Вечер (16-22 вечера)",
        "time_flexible": "Свободный график"
    }
    
    schedule = time_map[callback.data]
    await update_onboarding_data(callback.from_user.id, schedule=schedule)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🌱 Вегетарианство (без мяса)", callback_data="food_veg")
    builder.button(text="🥑 Веганство (без животных продуктов)", callback_data="food_vegan")
    builder.button(text="🍽️ Все ем", callback_data="food_all")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"3. Время тренировок: {schedule} ✅\n\n"
        "4/10 • Какие пищевые предпочтения?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка пищевых предпочтений
@router.callback_query(F.data.startswith("food_"))
async def process_food_preferences(callback: CallbackQuery, state: FSMContext):
    food_map = {
        "food_veg": "Вегетарианство (без мяса)",
        "food_vegan": "Веганство (без животных продуктов)",
        "food_all": "Все ем"
    }
    
    food_preferences = food_map[callback.data]
    await update_onboarding_data(callback.from_user.id, food_preferences=food_preferences)
    
    await callback.message.edit_text(
        f"4. Пищевые предпочтения: {food_preferences} ✅\n\n"
        "5/10 • Есть ли аллергии, непереносимости или ограничения в питании? Есть ли противопоказания врача, были ли травмы?\n"
        "Опиши подробнее (или напиши 'нет'):"
    )
    await state.set_state(QuestionnaireState.waiting_for_food_allergies)
    await callback.answer()

# Обработка аллергий
@router.message(QuestionnaireState.waiting_for_food_allergies, F.text)
async def process_food_allergies(message: Message, state: FSMContext):
    allergies = message.text if message.text.lower() != 'нет' else 'Нет противопоказаний'
    await update_onboarding_data(message.from_user.id, food_allergies=allergies)
    
    await message.answer(
        f"5. Аллергии и противопоказания: учтены ✅\n\n"
        "6/10 • Сколько тебе лет?\n"
        "Например: 25"
    )
    await state.set_state(QuestionnaireState.waiting_for_age_questionnaire)

# Обработка возраста
@router.message(QuestionnaireState.waiting_for_age_questionnaire, F.text)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if 10 <= age <= 100:
            await update_onboarding_data(message.from_user.id, age=age)
            
            await message.answer(
                f"6. Возраст: {age} ✅\n\n"
                "7/10 • Какой у тебя рост (в см)?\n"
                "Например: 180"
            )
            await state.set_state(QuestionnaireState.waiting_for_height_questionnaire)
        else:
            await message.answer("Пожалуйста, введите корректный возраст (10-100 лет):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 25):")

# Обработка роста
@router.message(QuestionnaireState.waiting_for_height_questionnaire, F.text)
async def process_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        if 100 <= height <= 250:
            await update_onboarding_data(message.from_user.id, height=height)
            
            await message.answer(
                f"7. Рост: {height} см ✅\n\n"
                "8/10 • Какой у тебя текущий вес (в кг)?\n"
                "Например: 75"
            )
            await state.set_state(QuestionnaireState.waiting_for_weight_questionnaire)
        else:
            await message.answer("Пожалуйста, введите корректный рост (100-250 см):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 180):")

# Обработка веса
@router.message(QuestionnaireState.waiting_for_weight_questionnaire, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if 30 <= weight <= 200:
            await update_onboarding_data(message.from_user.id, weight=weight)
            
            builder = InlineKeyboardBuilder()
            builder.button(text="💺 Сидячий образ жизни", callback_data="activity_low")
            builder.button(text="🚶‍♂️ Легкая активность (1-2 тренировки)", callback_data="activity_medium")
            builder.button(text="🏃‍♂️ Средняя активность (3-4 тренировки)", callback_data="activity_high")
            builder.button(text="🔥 Высокая активность (5+ тренировок)", callback_data="activity_extreme")
            builder.adjust(1)
            
            await message.answer(
                f"8. Вес: {weight} кг ✅\n\n"
                "9/10 • Какой у тебя уровень ежедневной активности?",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer("Пожалуйста, введите корректный вес (30-200 кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 75.5):")

# Обработка уровня активности
@router.callback_query(F.data.startswith("activity_"))
async def process_activity_level(callback: CallbackQuery, state: FSMContext):
    activity_map = {
        "activity_low": "Сидячий образ жизни",
        "activity_medium": "Легкая активность (1-2 тренировки)",
        "activity_high": "Средняя активность (3-4 тренировки)", 
        "activity_extreme": "Высокая активность (5+ тренировок)"
    }
    
    activity_level = activity_map[callback.data]
    await update_onboarding_data(callback.from_user.id, activity_level=activity_level)
    
    await callback.message.edit_text(
        f"9. Уровень активности: {activity_level} ✅\n\n"
        "10/10 • Сколько шагов в день в среднем проходишь?\n"
        "Например: 8000"
    )
    await state.set_state(QuestionnaireState.waiting_for_steps)
    await callback.answer()

# Обработка количества шагов
@router.message(QuestionnaireState.waiting_for_steps, F.text)
async def process_steps(message: Message, state: FSMContext):
    try:
        steps = int(message.text)
        if 1000 <= steps <= 50000:
            await update_onboarding_data(message.from_user.id, daily_steps=steps)
            
            # ЗАВЕРШАЕМ АНКЕТУ
            await complete_questionnaire(message.from_user.id)
            await state.clear()
            
        else:
            await message.answer("Пожалуйста, введите корректное количество шагов (1000-50000):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 8000):")

# ... продолжаем добавлять остальные вопросы аналогичным образом ...

# Завершение анкеты
async def complete_questionnaire(user_id: int):
    try:
        # Получаем все данные анкеты
        data = await get_full_onboarding_data(user_id)
        
        if not data:
            print(f"Нет данных анкеты для пользователя {user_id}")
            return
        
        # Формируем отчет для админа
        admin_report = create_admin_report(data)
        
        # Отправляем отчет админу
        await bot.send_message(
            config.ADMIN_ID,
            admin_report,
            parse_mode="Markdown"
        )
        
        # Уведомляем пользователя
        await bot.send_message(
            user_id,
            "🎉 *Анкета завершена!*\n\n"
            "Тренер уже анализирует твои ответы и готовит персональную программу!\n\n"
            "📋 *Важные шаги на завтра:*\n"
            "1. С утра сделай замеры в разделе «📊 Прогресс»\n"
            "2. Запиши текущие показатели (вес, объемы)\n"
            "3. Это поможет отслеживать прогресс!\n\n"
            "Программа будет готова в течение 24 часов! 💪"
        )
        
        # Показываем описание главного меню
        await asyncio.sleep(2)
        
        # Пробуем разные варианты импорта клавиатуры
        try:
            from keyboards.main_menu import get_main_keyboard as get_keyboard
        except ImportError:
            try:
                from keyboards.main_menu import get_main_menu as get_keyboard
            except ImportError:
                try:
                    from keyboards.main_menu import main_menu_kb as get_keyboard
                except ImportError:
                    # Если ничего не найдено, создаем простую клавиатуру
                    from aiogram.utils.keyboard import InlineKeyboardBuilder
                    def get_keyboard():
                        builder = InlineKeyboardBuilder()
                        builder.button(text="🍎 Питание", callback_data="nutrition")
                        builder.button(text="📊 Прогресс", callback_data="progress")
                        builder.button(text="💪 Упражнения", callback_data="exercises")
                        builder.button(text="❓ FAQ", callback_data="faq")
                        builder.button(text="📞 Поддержка", callback_data="support")
                        builder.adjust(2)
                        return builder.as_markup()
        
        await bot.send_message(
            user_id,
            "📱 *Главное меню бота:*\n\n"
            "🍎 *Питание* - рекомендации по питанию, КБЖУ\n"
            "📊 *Прогресс* - запись замеров и отслеживание результатов\n"
            "💪 *Упражнения* - техника выполнения упражнений\n"
            "❓ *FAQ* - ответы на частые вопросы\n"
            "📞 *Поддержка* - связь с тренером\n\n"
            "Выбирай раздел и начинай работу! 👇",
            reply_markup=get_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка при завершении анкеты: {e}")
        # Отправляем ошибку админу
        try:
            await bot.send_message(
                config.ADMIN_ID,
                f"❌ Ошибка при завершении анкеты для пользователя {user_id}:\n{str(e)}"
            )
        except Exception as admin_error:
            print(f"Не удалось отправить ошибку админу: {admin_error}")

def create_admin_report(data):
    """Создает подробный отчет для админа"""
    report = f"📋 *НОВАЯ АНКЕТА ДЛЯ ПРОГРАММЫ*\n\n"
    
    if data:
        report += f"👤 *Пользователь ID:* {data.get('user_id', 'N/A')}\n"
        report += f"📅 *Дата:* {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        report += f"*Основные данные:*\n"
        report += f"• Возраст: {data.get('age', 'Не указан')}\n"
        report += f"• Рост: {data.get('height', 'Не указан')} см\n"
        report += f"• Вес: {data.get('weight', 'Не указан')} кг\n"
        report += f"• Шаги в день: {data.get('daily_steps', 'Не указано')}\n\n"
        
        report += f"*Тренировки:*\n"
        report += f"• Опыт: {data.get('experience', 'Не указан')}\n"
        report += f"• Оборудование: {data.get('equipment', 'Не указано')}\n"
        report += f"• Время тренировок: {data.get('schedule', 'Не указано')}\n"
        report += f"• Уровень активности: {data.get('activity_level', 'Не указан')}\n\n"
        
        report += f"*Питание:*\n"
        report += f"• Предпочтения: {data.get('food_preferences', 'Не указаны')}\n"
        report += f"• Аллергии: {data.get('food_allergies', 'Нет')}\n\n"
        
        if data.get('health_issues') and data.get('health_issues') != 'Нет проблем со здоровьем':
            report += f"*Проблемы со здоровьем:*\n{data.get('health_issues')}\n\n"
        
        if data.get('motivation'):
            report += f"*Мотивация:*\n{data.get('motivation')}\n\n"
        
        report += f"#анкета #новыйклиент"
    
    return report

# Экспортируем router
__all__ = ['router', 'start_full_questionnaire']