from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from keyboards.main_menu import get_faq_keyboard
from database import get_faq_categories, get_faq_items, add_support_message, get_support_messages, update_support_message
from utils.bot_instance import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

router = Router()

class SupportResponse(StatesGroup):
    waiting_for_response = State()


# Состояния для добавления FAQ
class AddFAQItem(StatesGroup):
    waiting_for_category = State()
    waiting_for_question = State()
    waiting_for_answer = State()

# FAQ главное меню
@router.message(F.text == "❓ FAQ")
async def open_faq(message: Message):
    categories = await get_faq_categories()
    if not categories:
        await message.answer("ℹ️ Раздел FAQ пока пуст. Следите за обновлениями!")
        return
    
    text = "❓ *Часто задаваемые вопросы*\n\nВыберите категорию:"
    await message.answer(text, reply_markup=get_faq_categories_keyboard(categories))

def get_faq_categories_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        category_id, category_name, description = category
        builder.button(text=category_name, callback_data=f"faq_cat_{category_id}")
    builder.button(text="📞 Связь с тренером", callback_data="support_contact")
    builder.button(text="◀️ Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

@router.callback_query(F.data.startswith("faq_cat_"))
async def show_faq_category(callback: CallbackQuery):
    category_id = int(callback.data.replace("faq_cat_", ""))
    items = await get_faq_items(category_id)
    
    if not items:
        await callback.message.answer("В этой категории пока нет вопросов.")
        await callback.answer()
        return
    
    # Получаем название категории
    categories = await get_faq_categories()
    category_name = next((cat[1] for cat in categories if cat[0] == category_id), "Неизвестная категория")
    
    text = f"❓ *{category_name}*\n\nВыберите вопрос:"
    
    builder = InlineKeyboardBuilder()
    for item in items:
        item_id, question, answer, cat_name = item
        builder.button(text=question, callback_data=f"faq_item_{item_id}")
    
    builder.button(text="◀️ Назад к категориям", callback_data="faq_back")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("faq_item_"))
async def show_faq_answer(callback: CallbackQuery):
    item_id = int(callback.data.replace("faq_item_", ""))
    all_items = await get_faq_items()
    item = next((it for it in all_items if it[0] == item_id), None)
    
    if not item:
        await callback.message.answer("Вопрос не найден.")
        await callback.answer()
        return
    
    item_id, question, answer, category_name = item
    
    text = f"❓ *{question}*\n\n{answer}\n\n_Категория: {category_name}_"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад к вопросам", callback_data=f"faq_cat_{next((cat[0] for cat in await get_faq_categories() if cat[1] == category_name), '')}")
    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

# Команды для админа - добавление FAQ
@router.message(Command("addfaq"))
async def cmd_add_faq(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    categories = await get_faq_categories()
    if not categories:
        await message.answer("Сначала создайте категории через /addfaqcategory")
        return
    
    builder = InlineKeyboardBuilder()
    for category in categories:
        category_id, category_name, description = category
        builder.button(text=category_name, callback_data=f"addfaq_cat_{category_id}")
    
    builder.button(text="❌ Отмена", callback_data="admin_back")
    builder.adjust(1)
    
    await message.answer("Выберите категорию для нового вопроса:", reply_markup=builder.as_markup())
    await state.set_state(AddFAQItem.waiting_for_category)

@router.callback_query(F.data.startswith("addfaq_cat_"))
async def process_faq_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.replace("addfaq_cat_", ""))
    await state.update_data(category_id=category_id)
    await callback.message.answer("Введите вопрос:")
    await state.set_state(AddFAQItem.waiting_for_question)
    await callback.answer()

@router.message(AddFAQItem.waiting_for_question, F.text)
async def process_faq_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Введите ответ на вопрос:")
    await state.set_state(AddFAQItem.waiting_for_answer)

@router.message(AddFAQItem.waiting_for_answer, F.text)
async def process_faq_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_faq_item(data['category_id'], data['question'], message.text)
    await message.answer("✅ Вопрос добавлен в FAQ!")
    await state.clear()

# Команда для добавления категории
@router.message(Command("addfaqcategory"))
async def cmd_add_faq_category(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    parts = message.text.split(' ', 2)
    if len(parts) < 3:
        await message.answer("Использование: /addfaqcategory <название> <описание>")
        return
    
    category_name = parts[1]
    category_description = parts[2]
    
    await add_faq_category(category_name, category_description)
    await message.answer(f"✅ Категория '{category_name}' добавлена!")

# Кнопка "Назад" для FAQ
@router.callback_query(F.data == "faq_back")
async def faq_back(callback: CallbackQuery):
    categories = await get_faq_categories()
    text = "❓ *Часто задаваемые вопросы*\n\nВыберите категорию:"
    await callback.message.edit_text(text, reply_markup=get_faq_categories_keyboard(categories))
    await callback.answer()
    
@router.callback_query(F.data == "faq_main")
async def open_faq_callback(callback: CallbackQuery):
    categories = await get_faq_categories()
    if not categories:
        # Если категорий нет, предлагаем сразу связь с тренером
        text = (
            "ℹ️ Раздел FAQ пока пуст.\n\n"
            "Вы можете:\n"
            "• 📞 Связаться с тренером для получения помощи\n"
            "• 🎥 Посмотреть инструкцию по съемке упражнений\n"
            "• 📊 Узнать как вести отчеты"
        )
        await callback.message.edit_text(text, reply_markup=get_faq_keyboard())
        await callback.answer()
        return
    
    text = "❓ *Часто задаваемые вопросы*\n\nВыберите категорию:"
    await callback.message.edit_text(text, reply_markup=get_faq_categories_keyboard(categories))
    await callback.answer()
    
@router.message(Command("checkfaq"))
async def cmd_check_faq(message: Message):
    categories = await get_faq_categories()
    items = await get_faq_items()
    
    text = (
        f"📊 Статус FAQ:\n"
        f"• Категорий: {len(categories)}\n"
        f"• Вопросов: {len(items)}\n\n"
    )
    
    if categories:
        text += "📁 Категории:\n"
        for category in categories:
            category_id, category_name, description = category
            category_items = [item for item in items if item[3] == category_name]
            text += f"• {category_name}: {len(category_items)} вопросов\n"
    
    await message.answer(text)

# Добавляем обработчик для кнопки "Назад" из FAQ
@router.callback_query(F.data == "faq_back_to_main")
async def faq_back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("❓ Раздел «FAQ»:", reply_markup=get_faq_keyboard())
    await callback.answer()

# Добавляем обработчики для guide-кнопок
@router.callback_query(F.data == "faq_video_guide")
async def faq_video_guide(callback: CallbackQuery):
    text = (
        "🎥 *Как правильно снимать упражнения на видео:*\n\n"
        "✅ *Основные правила:*\n"
        "• Снимайте с нескольких ракурсов (спереди, сбоку, сзади)\n"
        "• Покажите всю амплитуду движения\n"
        "• Убедитесь, что хорошо видна техника выполнения\n"
        "• Оптимальная длительность: 15-30 секунд\n\n"
        "✅ *Рекомендации:*\n"
        "• Хорошее освещение\n"
        "• Стабильное положение камеры\n"
        "• Видны все части тела, участвующие в упражнении\n"
        "• Минимальные дрожания камеры"
    )
    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "faq_reports_guide")
async def faq_reports_guide(callback: CallbackQuery):
    text = (
        "📊 *Как вести отчеты:*\n\n"
        "✅ *Видеоотчеты:*\n"
        "• 1-2 раза в неделю\n"
        "• Показывайте технику сложных упражнений\n"
        "• Указывайте рабочие веса и ощущения\n\n"
        "✅ *Отчеты о питании:*\n"
        "• Ежедневно\n"
        "• Описывайте все приемы пищи\n"
        "• Указывайте примерные объемы\n"
        "• Не забывайте про воду\n\n"
        "✅ *Отчеты о состоянии:*\n"
        "• По необходимости\n"
        "• Описывайте самочувствие\n"
        "• Указывайте проблемы или успехи\n"
        "• Сообщайте о болях или дискомфорте"
    )
    await callback.message.edit_text(text)
    await callback.answer()