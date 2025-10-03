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
        "Я — твой персональный бот-помощник для онлайн ведения.\n\n"
        "Я буду записывать твои замеры,подскажу с рецептами, упражнениями, напомню об оплатах и многое другое\n\n"
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
        pdf_path = '/gym_trainer_bot/Меню на сушке.pdf'
        
        if not os.path.exists(pdf_path):
            await callback.message.answer("❌ Файл с меню временно недоступен. Мы уже работаем над исправлением!")
            logging.error(f"PDF файл не найден: {pdf_path}")
            await callback.answer()
            return
        
        # Отправляем PDF файл
        pdf_file = FSInputFile(pdf_path, filename="Рацион на день.pdf")
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
        "1. 🍎 *Индивидуальный план питания* - 25 BYN\n"
        "   • Персональный рацион под твои цели\n"
        "   • Учет аллергий и предпочтений\n"
        "   • Готов в течение 24 часов\n\n"
        "2. 🏋️ *Полное онлайн-ведение* - 100 BYN/месяц\n"
        "   • Персональные тренировки\n"
        "   • Питание + тренировки\n"
        "   • Ежедневная поддержка тренера\n"
        "   • Отслеживание прогресса\n\n"
        "Что тебя интересует?"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🍎 Индивидуальное питание (25 BYN)", callback_data="option_nutrition")
    builder.button(text="🏋️ Полное ведение (100 BYN/месяц)", callback_data="option_full")
    builder.button(text="🤔 Сначала узнать подробнее", callback_data="option_info")
    builder.adjust(1)
    
    await message.answer(options_text, reply_markup=builder.as_markup())

# Информация о вариантах
@router.callback_query(F.data == "option_info")
async def show_detailed_info(callback: CallbackQuery):
    info_text = (
        "📋 *Подробнее о вариантах:*\n\n"
        "🍎 *Индивидуальный план питания (25 BYN)*:\n"
        "• Анкета из 4 вопросов\n"
        "• Рацион на 2 недели\n"
        "• Учет твоих предпочтений\n"
        "• Рекомендации по приготовлению\n\n"
        "🏋️ *Полное онлайн-ведение (100 BYN/месяц)*:\n"
        "• Персональная программа тренировок\n"
        "• Индивидуальный план питания\n"
        "• Ежедневная поддержка в чате\n"
        "• Коррекция программ\n"
        "• Отслеживание прогресса\n"
        "• Мотивация и контроль\n\n"
        "Выбирай то, что подходит именно тебе! 👇"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🍎 План питания - 25 BYN", callback_data="option_nutrition")
    builder.button(text="🏋️ Полное ведение - 100 BYN", callback_data="option_full")
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
        "Отлично! 🍎\n"
        "Создам для тебя персональный план питания всего за 25 BYN!\n\n"
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
        "2/4 • Есть ли у тебя аллергии или пищевые ограничения?",
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
        f"Аллергии/ограничения: {allergy_text} 👍\n\n"
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
                    "6/6 • Какие именно у тебя аллергии или ограничения?\n"
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
        "💳 *Для получения плана питания:*\n"
        "1. Оплати 25 BYN на карту:\n"
        "   • Номер: 1111 2222 3333 4444\n"
        "   • Получатель: Иван Иванов\n"
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
        "🏋️ *Полное онлайн-ведение - 100 BYN/месяц*\n\n"
        "Что входит:\n"
        "✅ Персональная программа тренировок\n"
        "✅ Индивидуальный план питания\n"
        "✅ Ежедневная поддержка в чате\n"
        "✅ Коррекция программ по мере прогресса\n"
        "✅ Отслеживание результатов\n"
        "✅ Мотивация и ответы на вопросы\n\n"
        "После оплаты ты получишь:\n"
        "1. Доступ ко всем разделам бота\n"
        "2. Анкету для составления программ\n"
        "3. Персональный план на первый месяц\n"
        "4. Постоянную поддержку тренера\n\n"
        "💳 *Как оплатить:*\n"
        "1. Переведи 100 BYN на карту:\n"
        "   • Номер: 1111 2222 3333 4444\n"
        "   • Получатель: Иван Иванов\n"
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

# Обработка оплаты полного ведения
@router.callback_query(F.data == "pay_full")
async def handle_full_payment(callback: CallbackQuery):
    payment_instructions = (
        "💳 *Оплата полного ведения*\n\n"
        "Сумма: 100 BYN/месяц\n"
        "Карта: 1111 2222 3333 4444\n"
        "Получатель: Иван Иванов\n\n"
        "После оплаты:\n"
        "1. Пришли скриншот перевода\n"
        "2. Получи доступ к боту\n"
        "3. Заполни подробную анкету\n"
        "4. Получи персональную программу!\n\n"
        "Оплатил? Присылай скриншот! 📸"
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
            admin_caption = f"💰 *ОПЛАТА ПЛАНА ПИТАНИЯ* (25 BYN)\n\n👤 {message.from_user.full_name}"
        else:
            # Это оплата полного ведения
            product_type = 'full'
            user_message = "✅ Скриншот получен! Проверяю оплату..."
            admin_caption = f"💰 *ОПЛАТА ПОЛНОГО ВЕДЕНИЯ* (100 BYN)\n\n👤 {message.from_user.full_name}"
        
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
        "Сумма: 100 BYN/месяц\n"
        "Карта: 1111 2222 3333 4444\n"
        "Получатель: Иван Иванов\n\n"
        "*В комментарии укажи:* \"Полное ведение\"\n\n"
        "После оплаты пришли скриншот перевода 📸"
    )
    
    await callback.message.edit_text(payment_instructions)
    await callback.answer()