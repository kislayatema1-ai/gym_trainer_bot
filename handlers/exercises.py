from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
from database import get_exercise_videos, get_exercise_literature, add_exercise_video, add_exercise_literature
from utils.bot_instance import bot
import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# Состояния для добавления материалов (админ)
class AddExerciseVideo(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_video = State()

class AddLiterature(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_category = State()
    waiting_for_file = State()

# Состояния для добавления YouTube видео
class AddYouTubeVideo(StatesGroup):
    waiting_for_name = State()
    waiting_for_url = State()
    waiting_for_description = State()
    waiting_for_category = State()

# Видеоуроки - улучшенная версия
@router.callback_query(F.data == "exercises_videos")
async def show_exercise_videos(callback: CallbackQuery):
    videos = await get_exercise_videos()
    if not videos:
        await callback.message.answer("🎥 Видеоуроки пока не добавлены. Следите за обновлениями!")
        await callback.answer()
        return
    
    # Группируем видео по категориям
    categories = {}
    for video in videos:
        name, file_id, description, category = video
        if category not in categories:
            categories[category] = []
        categories[category].append((name, file_id, description))
    
    # Отправляем сообщение с выбором категории
    text = "🎥 *Выберите категорию упражнений:*\n\n"
    for category in categories.keys():
        text += f"• {category}\n"
    
    await callback.message.answer(text, reply_markup=get_video_categories_keyboard(categories.keys()))
    await callback.answer()

def get_video_categories_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"video_cat_{category}")
    builder.button(text="◀️ Назад", callback_data="exercises_back")
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(F.data.startswith("video_cat_"))
async def show_videos_by_category(callback: CallbackQuery):
    category = callback.data.replace("video_cat_", "")
    videos = await get_exercise_videos(category)
    
    if not videos:
        await callback.message.answer(f"В категории '{category}' пока нет видеоуроков.")
        await callback.answer()
        return
    
    # Создаем клавиатуру с упражнениями
    builder = InlineKeyboardBuilder()
    for video in videos:
        name, file_id, description = video
        builder.button(text=name, callback_data=f"ex_video_{file_id}")
    
    builder.button(text="◀️ Назад к категориям", callback_data="exercises_videos")
    builder.adjust(1)
    
    await callback.message.answer(f"🎥 Упражнения - *{category}*:\n\nВыберите упражнение:", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("ex_video_"))
async def send_exercise_video(callback: CallbackQuery):
    file_id = callback.data.replace("ex_video_", "")
    
    # Находим видео по file_id
    videos = await get_exercise_videos()
    for video in videos:
        name, vid_file_id, description, category = video
        if vid_file_id == file_id:
            try:
                await callback.message.answer_video(video=file_id, caption=f"🏋️ *{name}*\n\n{description}\n\nКатегория: {category}")
                await callback.answer()
                return
            except Exception as e:
                await callback.message.answer(f"❌ Не удалось отправить видео. Ошибка: {e}")
                await callback.answer()
                return
    
    await callback.message.answer("❌ Видео не найдено.")
    await callback.answer()

# Советы и литература - улучшенная версия
@router.callback_query(F.data == "exercises_literature")
async def show_exercise_literature(callback: CallbackQuery):
    literature = await get_exercise_literature()
    if not literature:
        await callback.message.answer("📚 Материалы пока не добавлены. Следите за обновлениями!")
        await callback.answer()
        return
    
    # Группируем материалы по категориям
    categories = {}
    for doc in literature:
        title, file_id, description, category = doc
        if category not in categories:
            categories[category] = []
        categories[category].append((title, file_id, description))
    
    text = "📚 *Выберите категорию материалов:*\n\n"
    for category in categories.keys():
        text += f"• {category}\n"
    
    await callback.message.answer(text, reply_markup=get_literature_categories_keyboard(categories.keys()))
    await callback.answer()

def get_literature_categories_keyboard(categories):
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"doc_cat_{category}")
    builder.button(text="◀️ Назад", callback_data="exercises_back")
    builder.adjust(2)
    return builder.as_markup()

@router.callback_query(F.data.startswith("doc_cat_"))
async def show_literature_by_category(callback: CallbackQuery):
    category = callback.data.replace("doc_cat_", "")
    docs = await get_exercise_literature(category)
    
    if not docs:
        await callback.message.answer(f"В категории '{category}' пока нет материалов.")
        await callback.answer()
        return
    
    # Создаем клавиатуру с материалами
    builder = InlineKeyboardBuilder()
    for doc in docs:
        title, file_id, description = doc
        builder.button(text=title, callback_data=f"ex_doc_{file_id}")
    
    builder.button(text="◀️ Назад к категориям", callback_data="exercises_literature")
    builder.adjust(1)
    
    await callback.message.answer(f"📚 Материалы - *{category}*:\n\nВыберите материал:", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("ex_doc_"))
async def send_exercise_document(callback: CallbackQuery):
    file_id = callback.data.replace("ex_doc_", "")
    
    # Находим документ по file_id
    docs = await get_exercise_literature()
    for doc in docs:
        title, doc_file_id, description, category = doc
        if doc_file_id == file_id:
            try:
                await callback.message.answer_document(document=file_id, caption=f"📄 *{title}*\n\n{description}\n\nКатегория: {category}")
                await callback.answer()
                return
            except Exception as e:
                await callback.message.answer(f"❌ Не удалось отправить документ. Ошибка: {e}")
                await callback.answer()
                return
    
    await callback.message.answer("❌ Документ не найден.")
    await callback.answer()

# Работа с инвентарем
@router.callback_query(F.data == "exercises_equipment")
async def show_equipment_guide(callback: CallbackQuery):
    text = (
        "🧤 *Работа с инвентарем:*\n\n"
        "✅ *Пояса:*\n• Используйте для тяжелых приседаний и становой тяги\n• Не затягивайте слишком туго\n• Располагайте на уровне пупка\n\n"
        "✅ *Перчатки:*\n• Защищают от мозолей\n• Улучшают хват\n• Выбирайте с хорошей вентиляцией\n\n"
        "✅ *Лямки:*\n• Для тяговых упражнений\n• Помогают при слабом хвате\n• Не используйте постоянно\n\n"
        "✅ *Кистевые бинты:*\n• Для жимовых упражнений\n• Поддерживают запястья\n• Не затягивайте слишком туго\n\n"
        "💡 *Для индивидуальных рекомендаций по инвентарю обратитесь к тренеру.*"
    )
    await callback.message.answer(text)
    await callback.answer()

# Кнопка "Назад" для упражнений
@router.callback_query(F.data == "exercises_back")
async def exercises_back(callback: CallbackQuery):
    await callback.message.edit_text("📚 Раздел «Упражнения»:", reply_markup=get_exercises_keyboard())
    await callback.answer()

# Команды для админа (добавление упражнений)
@router.message(Command("addexercise"))
async def cmd_add_exercise(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    await message.answer("Введите название упражнения:")
    await state.set_state(AddExerciseVideo.waiting_for_name)

# Команда для добавления YouTube видео
@router.message(Command("addyoutube"))
async def cmd_add_youtube(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    await message.answer("Введите название упражнения:")
    await state.set_state(AddYouTubeVideo.waiting_for_name)

@router.message(AddYouTubeVideo.waiting_for_name, F.text)
async def process_yt_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите YouTube ссылку (например: https://youtu.be/xxxxxx):")
    await state.set_state(AddYouTubeVideo.waiting_for_url)

@router.message(AddYouTubeVideo.waiting_for_url, F.text)
async def process_yt_url(message: Message, state: FSMContext):
    if "youtube.com" not in message.text and "youtu.be" not in message.text:
        await message.answer("Пожалуйста, введите корректную YouTube ссылку.")
        return
    
    await state.update_data(url=message.text)
    await message.answer("Введите описание упражнения:")
    await state.set_state(AddYouTubeVideo.waiting_for_description)

@router.message(AddYouTubeVideo.waiting_for_description, F.text)
async def process_yt_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    
    # Предлагаем выбрать категорию
    categories = ["Грудь", "Спина", "Ноги", "Плечи", "Руки", "Пресс", "Кардио", "Растяжка"]
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"yt_cat_{category}")
    
    await message.answer("Выберите категорию:", reply_markup=builder.as_markup())
    await state.set_state(AddYouTubeVideo.waiting_for_category)

@router.callback_query(F.data.startswith("yt_cat_"))
async def process_yt_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("yt_cat_", "")
    data = await state.get_data()
    
    await add_youtube_video(data['name'], data['url'], data['description'], category)
    await callback.message.answer(f"✅ YouTube видео '{data['name']}' добавлено в категорию '{category}'!")
    await state.clear()
    await callback.answer()

# ... остальные команды админа можно добавить позже

# Удаляем старый обработчик, который мешал работе
@router.message(F.text)
async def handle_text_message(message: Message):
    # Этот обработчик может конфликтовать с другими, лучше его убрать
    # или сделать более специфичным
    pass