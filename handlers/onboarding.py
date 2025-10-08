import os
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import init_user_onboarding, update_onboarding_data, get_onboarding_data, check_user_access, add_payment
from utils.bot_instance import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

router = Router()

# Состояния для onboarding
class OnboardingState(StatesGroup):
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_age = State()
    waiting_for_allergies_details = State()
    waiting_for_experience = State()
    waiting_for_equipment = State()
    waiting_for_schedule = State()
    waiting_for_food_preferences = State()
    waiting_for_health_issues = State()
    waiting_for_onboarding_screenshot = State()

# ОТДЕЛЬНЫЕ состояния для полной анкеты (чтобы не конфликтовали)
class FullQuestionnaireState(StatesGroup):
    waiting_for_full_height = State()
    waiting_for_full_weight = State()
    waiting_for_full_age = State()
    waiting_for_full_experience = State()
    waiting_for_full_equipment = State()
    waiting_for_full_schedule = State()
    waiting_for_full_goals = State()
    waiting_for_full_health = State()
    waiting_for_full_food_preferences = State()

# Функция для показа контактов тренера
async def show_trainer_contacts(message: Message):
    contact_text = (
        "📞 *Связь с тренером:*\n\n"
        f"👤 Telegram: {config.ADMIN_USERNAME}\n"
        f"📱 Телефон: {config.ADMIN_CONTACT}\n"
        "⏰ Время ответа: 1-2 часа\n\n"
        "Не стесняйся задавать вопросы! 💪"
    )
    await message.answer(contact_text)

# Приветственное сообщение с предложением подарка
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # Добавляем пользователя в базу
    from database import add_user
    await add_user(user_id, username, full_name)
    
    # Инициализируем onboarding
    await init_user_onboarding(user_id)
    
    # Отправляем приветственное сообщение
    welcome_text = (
        f"Привет, {full_name}! 👋\n\n"
        "Я — помощник тренера Анастасии. ❤️\n"
        "Я делаю ваше сотрудничество более удобным! Я храню таблицы ваших тренировок, имею базу уроков по упражнениям, у меня большой раздел который поможет тебе следить за воим питание, следить за оплатами и другие полезные функции, я буду обновляться и со временем улучшать свои разделы, а если у тебя будут пожелания то сообщай о них Насте.\n\n"
        "Так же Анастасия может написать для тебя персональную программу тренировок, для этого не нужно иметь доступ к боту, а просто выбрать этот вариант из предложенных позже\n"
        "🎁 *В подарок для тебя:*\n"
        "Рацион на день - совершенно бесплатно!\n\n"
        "Хочешь получить файл с рационом?"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, хочу подарок!", callback_data="onboarding_get_pdf")
    builder.button(text="❌ Нет, спасибо", callback_data="onboarding_skip_pdf")
    builder.adjust(1)
    
    await message.answer(welcome_text, reply_markup=builder.as_markup())

# Отправка PDF
@router.callback_query(F.data == "onboarding_get_pdf")
async def send_pdf_file(callback: CallbackQuery):
    try:
        # ИСПРАВЛЕННЫЙ ПУТЬ - абсолютный путь на сервере
        pdf_path = '/root/gym_trainer_bot/menu.pdf'
        
        if not os.path.exists(pdf_path):
            await callback.message.answer("❌ Файл с меню временно недоступен. Мы уже работаем над исправлением!")
            logging.error(f"PDF файл не найден: {pdf_path}")
            await callback.answer()
            return
        
        # Отправляем PDF файл
        pdf_file = FSInputFile(pdf_path, filename="menu.pdf")
        await callback.message.answer_document(
            pdf_file,
            caption="🎁 *Твой подарок!*\n\n"
                   "📋 Рацион на день\n\n"
                   "Сохрани файл и используй его! "
                   "Это отличная основа для начала правильного питания."
        )
        
        # Обновляем статус в базе
        await update_onboarding_data(callback.from_user.id, received_pdf=1)
        
        # Устанавливаем время для follow-up вопроса через 24 часа
        next_question_date = datetime.datetime.now() + datetime.timedelta(hours=24)
        await update_onboarding_data(callback.from_user.id, next_question_date=next_question_date.isoformat())
        
        # Предлагаем возможности бота
        await show_bot_options(callback.message)
        
    except Exception as e:
        await callback.message.answer("❌ Не удалось отправить файл. Свяжитесь с тренером.")
        print(f"PDF sending error: {e}")
    
    await callback.answer()

# Пропуск PDF
@router.callback_query(F.data == "onboarding_skip_pdf")
async def skip_pdf(callback: CallbackQuery):
    await callback.message.answer(
        "Хорошо! Если передумаешь - всегда можешь попросить рацион у тренера.\n\n"
        "Давай я расскажу тебе о других возможностях! 👇"
    )
    
    # Предлагаем возможности бота
    await show_bot_options(callback.message)
    await callback.answer()

# Показ вариантов после получения/пропуска PDF
async def show_bot_options(message: Message):
    options_text = (
        "✨ *Что я могу предложить:*\n\n"
        "1. 🏋️ *Индивидуальный план тренировок* - 50 BYN\n"
        "   • Персональные тренировки под твои цели\n"
        "   • Учет предпочтений\n"
        "   • Готов в течение 24 часов\n\n"
        "2. 🏋️ *Полное онлайн-ведение* - 200 BYN/месяц\n"
        "   • Персональные тренировки\n"
        "   • Питание + тренировки\n"
        "   • Ежедневная поддержка тренера\n"
        "   • И многое другое\n\n"
        "Что тебя интересует?"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏋️ Индивидуальный план тренировок (50 BYN)", callback_data="option_nutrition")
    builder.button(text="🏋️ Полное ведение (200 BYN/месяц)", callback_data="option_full")
    builder.button(text="🤔 Сначала узнать подробнее", callback_data="option_info")
    builder.adjust(1)
    
    await message.answer(options_text, reply_markup=builder.as_markup())

# Информация о вариантах
@router.callback_query(F.data == "option_info")
async def show_detailed_info(callback: CallbackQuery):
    info_text = (
        "📋 *Подробнее о вариантах:*\n\n"
        "🏋️ *Индивидуальный план тренировок (50 BYN)*:\n"
        "• Анкета из 4 вопросов\n"
        "• Тренировочный план для твоих самостоятельных тренировок в зале\n"
        "• Учет твоих предпочтений\n"
        "• Рекомендации по использованию\n\n"
        "🏋️ *Полное онлайн-ведение (200 BYN/месяц)*:\n"
        "• Персональная программа тренировок подготовленная под твои цели и желания\n"
        "• У нас удобные таблицы и приятный интерфейс, забудь о блокнотах и не напрягай память\n"
        "• Система видеотчетов с проверкой вашей техники выполнения упражнений\n"
        "• Ведение и коррекция твоего питания, в боте есть база с советами по питанию\n"
        "• Этот бот дает доступ к большой библиотеке рецептов с расчитанной калорийностью, просто бери продукты и готовь!\n"
        "• Постоянная связь с тренером, бот всего лишь помогает вам в каких то вопросах\n"
        "• Встроена система уведомлений оплат (У вас с тренером не будет путаницы когда нужно оплатить ведение)\n"
        "• Коррекция программ\n"
        "• Отслеживание прогресса\n"
        "• Мотивация, психологическая поддержка и контроль\n\n"
        "Выбирай то, что подходит именно тебе! 👇"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏋️ План тренировок - 50 BYN", callback_data="option_nutrition")
    builder.button(text="🏋️ Полное ведение - 200 BYN", callback_data="option_full")
    builder.adjust(1)
    
    await callback.message.edit_text(info_text, reply_markup=builder.as_markup())
    await callback.answer()

# Обработка кнопки "Сначала задать вопрос"
@router.callback_query(F.data == "ask_question")
async def handle_ask_question(callback: CallbackQuery):
    await show_trainer_contacts(callback.message)
    await callback.answer()

# Выбор индивидуального питания
@router.callback_query(F.data == "option_nutrition")
async def start_nutrition_questionnaire(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отлично! 🏋️\n"
        "Создам для тебя персональный план тренировок всего за 50 BYN!\n\n"
        "Ответь на 4 простых вопроса:"
    )
    
    # Первый вопрос - цели (вертикальные кнопки)
    builder = InlineKeyboardBuilder()
    builder.button(text="🍃 Похудеть", callback_data="goal_lose")
    builder.button(text="💪 Набрать массу", callback_data="goal_gain") 
    builder.button(text="❤️ Улучшить здоровье", callback_data="goal_health")
    builder.button(text="⚖️ Поддерживать вес", callback_data="goal_maintain")
    builder.adjust(1)
    
    await callback.message.answer(
        "1/4 • Какая у тебя основная цель?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка цели (вертикальные кнопки)
@router.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal_map = {
        "goal_lose": "похудеть",
        "goal_gain": "набрать массу", 
        "goal_health": "улучшить здоровье",
        "goal_maintain": "поддерживать вес"
    }
    
    goal = goal_map[callback.data]
    await state.update_data(goal=goal)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="allergies_yes")
    builder.button(text="❌ Нет", callback_data="allergies_no")
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"Цель: {goal} 👍\n\n"
        "2/4 • Есть ли у тебя ограничения по здоровью или запреты врачей связанные со спортом?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка аллергий
@router.callback_query(F.data.startswith("allergies_"))
async def process_allergies(callback: CallbackQuery, state: FSMContext):
    has_allergies = 1 if callback.data == "allergies_yes" else 0
    await state.update_data(allergies=has_allergies)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="0-1 раз в неделю", callback_data="freq_01")
    builder.button(text="2-3 раза в неделю", callback_data="freq_23")
    builder.button(text="4+ раза в неделю", callback_data="freq_4plus")
    builder.adjust(1)
    
    allergy_text = "есть" if has_allergies else "нет"
    await callback.message.edit_text(
        f"Здоровье/ограничения: {allergy_text} 👍\n\n"
        "3/4 • Как часто ты тренируешься?",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# Обработка частоты тренировок
@router.callback_query(F.data.startswith("freq_"))
async def process_training_frequency(callback: CallbackQuery, state: FSMContext):
    freq_map = {
        "freq_01": "0-1 раз в неделю",
        "freq_23": "2-3 раза в неделю", 
        "freq_4plus": "4+ раза в неделю"
    }
    
    frequency = freq_map[callback.data]
    await state.update_data(training_frequency=frequency)
    
    await callback.message.edit_text(
        f"Тренировки: {frequency} 👍\n\n"
        "4/6 • Какой у тебя рост (в см)?\n"
        "Например: 180"
    )
    await state.set_state(OnboardingState.waiting_for_height)
    await callback.answer()

# Обработка роста
@router.message(OnboardingState.waiting_for_height, F.text)
async def process_height(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        if 100 <= height <= 250:
            await state.update_data(height=height)
            
            await message.answer(
                f"Рост: {height} см 👍\n\n"
                "5/6 • Какой у тебя текущий вес (в кг)?\n"
                "Например: 75"
            )
            await state.set_state(OnboardingState.waiting_for_weight)
        else:
            await message.answer("Пожалуйста, введите корректный рост (100-250 см):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 180):")

# Обработка веса
@router.message(OnboardingState.waiting_for_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if 30 <= weight <= 200:
            await state.update_data(weight=weight)
            
            data = await state.get_data()
            if data.get('allergies') == 1:
                await message.answer(
                    f"Вес: {weight} кг 👍\n\n"
                    "6/6 • Какие именно у тебя запреты или ограничения?\n"
                    "Опиши подробнее:"
                )
                await state.set_state(OnboardingState.waiting_for_allergies_details)
            else:
                await complete_nutrition_questionnaire(message, state)
        else:
            await message.answer("Пожалуйста, введите корректный вес (30-200 кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 75.5):")

# Обработка деталей аллергий
@router.message(OnboardingState.waiting_for_allergies_details, F.text)
async def process_allergies_details(message: Message, state: FSMContext):
    data = await state.get_data()
    await complete_nutrition_questionnaire(message, state, message.text)

# Завершение анкеты питания
async def complete_nutrition_questionnaire(message: Message, state: FSMContext, allergies_details=None):
    data = await state.get_data()
    
    await update_onboarding_data(
        message.from_user.id,
        goal=data.get('goal'),
        allergies=data.get('allergies'),
        allergies_details=allergies_details,
        training_frequency=data.get('training_frequency'),
        height=data.get('height'),
        weight=data.get('weight')
    )
    
    payment_text = (
        "🎉 Анкета заполнена! Спасибо!\n\n"
        "💳 *Для получения плана тренировок:*\n"
        "1. Оплати 50 BYN на карту:\n"
        "   • Номер: 5299 2299 3689 8638\n"
        "2. Пришли скриншот оплаты\n"
        "3. Получи план питания в течение 24 часов!\n\n"
        "Оплатил? Присылай скриншот! 📸"
    )
    
    await message.answer(payment_text)
    await state.set_state(OnboardingState.waiting_for_onboarding_screenshot)

# Выбор полного ведения
@router.callback_query(F.data == "option_full")
async def start_full_onboarding(callback: CallbackQuery):
    full_info_text = (
        "🏋️ *Полное онлайн-ведение - 200 BYN/месяц*\n\n"
        "Что входит:\n"
        "✅ Персональная программа тренировок, проверка видеоотчетов, коррекция техники\n"
        "✅ Ведение вашего питания, калорийность, библиотека рецептов\n"
        "✅ Постоянная связь с тренером\n"
        "✅ Коррекция программ по мере прогресса\n"
        "✅ Отслеживание результатов\n"
        "✅ Мотивация, поддержка и ответы на вопросы\n\n"
        "После оплаты ты получишь:\n"
        "1. Доступ ко всем разделам бота\n"
        "2. Анкету для составления программ\n"
        "3. Персональный план на первый месяц\n"
        "4. Постоянную поддержку тренера\n\n"
        "💳 *Как оплатить:*\n"
        "1. Переведи 200 BYN на карту:\n"
        "   • Номер: 5299 2299 3689 8638\n"
        "2. Пришли скриншот оплаты\n"
        "3. Получи полный доступ и анкету!\n\n"
        "Готов начать изменения? 💪"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить полное ведение", callback_data="pay_full")
    builder.button(text="📞 Сначала задать вопрос", callback_data="ask_question")
    builder.adjust(1)
    
    await callback.message.edit_text(full_info_text, reply_markup=builder.as_markup())
    await callback.answer()

# Обработка оплаты полного ведения из onboarding
@router.callback_query(F.data == "pay_full")
async def handle_full_payment(callback: CallbackQuery, state: FSMContext):
    payment_instructions = (
        "💳 *Оплата полного ведения*\n\n"
        "Сумма: 200 BYN/месяц\n"
        "Карта: 5299 2299 3689 8638\n"
        "*В комментарии укажи:* \"Полное ведение\"\n\n"
        "После оплаты:\n"
        "1. Пришли скриншот перевода 📸\n"  
        "2. Сразу получишь доступ к боту\n"
        "3. Заполнишь подробную анкету\n"
        "4. Получишь персональную программу!\n\n"
        "Оплатил? Присылай скриншот!"
    )
    
    await callback.message.edit_text(payment_instructions)
    await callback.answer()

@router.message(F.photo)
async def handle_onboarding_payment_screenshot(message: Message, state: FSMContext):
    try:
        screenshot_id = message.photo[-1].file_id
        
        # Определяем тип платежа по контексту
        current_state = await state.get_state()
        user_data = await state.get_data()
        
        product_type = 'full'  # по умолчанию полное ведение
        
        # Если это из анкеты питания или есть данные о цели - это план питания
        if (current_state == OnboardingState.waiting_for_onboarding_screenshot or 
            'goal' in user_data):
            product_type = 'nutrition'
            user_message = "✅ Скриншот получен! План питания будет отправлен после проверки оплаты."
            admin_caption = f"💰 *ОПЛАТА ПЛАНА ТРЕНИРОВОК* (50 BYN)\n\n👤 {message.from_user.full_name}"
        else:
            # Это оплата полного ведения из onboarding
            product_type = 'full'
            user_message = "✅ Скриншот получен! Проверяю оплату..."
            admin_caption = f"💰 *ОПЛАТА ПОЛНОГО ВЕДЕНИЯ* (200 BYN)\n\n👤 {message.from_user.full_name}"
            
            # ЗАПУСКАЕМ АНКЕТУ СРАЗУ для onboarding потока
            await start_full_onboarding_questionnaire(message.from_user.id)
        
        await message.answer(user_message)
        
        # Сохраняем в базу с указанием типа продукта
        from database import add_payment
        await add_payment(message.from_user.id, screenshot_id, product_type)
        
        # Уведомляем админа с разными текстами
        from keyboards.main_menu import get_admin_payment_decision_kb
        full_admin_text = (
            f"{admin_caption}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"📅 Время: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
            f"📸 Скриншот:"
        )
        
        await bot.send_photo(
            chat_id=config.ADMIN_ID,
            photo=screenshot_id,
            caption=full_admin_text,
            reply_markup=get_admin_payment_decision_kb(message.from_user.id, product_type)  # Передаем тип продукта
        )
        
    except Exception as e:
        await message.answer("❌ Ошибка обработки. Свяжитесь с тренером.")
        print(f"Payment error: {e}")

# Добавляем кнопку для оплаты в onboarding
@router.callback_query(F.data == "pay_full")
async def handle_full_payment(callback: CallbackQuery):
    payment_instructions = (
        "💳 *Оплата полного ведения*\n\n"
        "Сумма: 200 BYN/месяц\n"
        "Карта: 5299 2299 3689 8638\n"
        "*В комментарии укажи:* \"Полное ведение\"\n\n"
        "После оплаты пришли скриншот перевода 📸"
    )
    
    await callback.message.edit_text(payment_instructions)
    await callback.answer()

async def start_full_questionnaire(user_id: int):
    """Запускает полную анкету для нового пользователя (для payment.py)"""
    try:
        from utils.bot_instance import bot
        
        # Отправляем приветственное сообщение с анкетой
        welcome_text = (
            "🎉 *Добро пожаловать в полное ведение!*\n\n"
            "Давай заполним подробную анкету, чтобы я мог составить для тебя персональную программу тренировок и питания!\n\n"
            "Готов начать? 💪"
        )
        
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Начать анкету", callback_data="start_full_questionnaire")
        builder.adjust(1)
        
        await bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        print(f"Ошибка при запуске анкеты: {e}")
        raise e

@router.callback_query(F.data == "start_full_questionnaire")
async def handle_start_full_questionnaire(callback: CallbackQuery, state: FSMContext):
    """Начинает полную анкету для полного ведения"""
    # Очищаем состояние на всякий случай
    await state.clear()
    
    await callback.message.answer(
        "Отлично! 🏋️\n"
        "Заполним подробную анкету для твоей персональной программы!\n\n"
        "📏 *1/9* • Какой у тебя рост (в см)?\n"
        "Например: 180"
    )
    await state.set_state(FullQuestionnaireState.waiting_for_full_height)
    await callback.answer()

async def start_full_onboarding_questionnaire(user_id: int):
    """Запускает полную анкету сразу после оплаты в onboarding потоке"""
    try:
        from utils.bot_instance import bot
        
        # Даем доступ пользователю
        from database import update_user_access
        new_access_date = await update_user_access(user_id, 30)
        
        # Отправляем приветственное сообщение с анкетой
        welcome_text = (
            "🎉 *Оплата получена! Добро пожаловать в полное ведение!*\n\n"
            f"✅ Твой доступ активирован до {new_access_date}\n\n"
            "Теперь заполним подробную анкету, чтобы я мог составить для тебя персональную программу тренировок и питания!\n\n"
            "Готов начать? 💪"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=welcome_text
        )
        
        # ЗАПУСКАЕМ АНКЕТУ ИЗ questionnaire.py
        from handlers.questionnaire import start_full_questionnaire
        await start_full_questionnaire(user_id)
        
    except Exception as e:
        print(f"Ошибка при запуске анкеты onboarding: {e}")
        # В случае ошибки все равно отправляем сообщение
        from utils.bot_instance import bot
        await bot.send_message(
            chat_id=user_id,
            text="🎉 Оплата получена! Но произошла техническая ошибка. Свяжитесь с тренером для получения анкеты."
        )
        raise e