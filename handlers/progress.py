from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_progress_data, get_progress_data, get_last_weight, add_achievement, get_achievements, check_user_access
from utils.bot_instance import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime
import matplotlib.pyplot as plt
import io
import numpy as np

router = Router()

# Состояния для добавления прогресса
class ProgressState(StatesGroup):
    waiting_for_weight = State()
    waiting_for_chest = State()
    waiting_for_waist = State()
    waiting_for_hips = State()
    waiting_for_arms = State()
    waiting_for_notes = State()

# Главное меню прогресса
@router.callback_query(F.data == "progress_main")
async def progress_main(callback: CallbackQuery):
    if not await check_user_access(callback.from_user.id):
        await callback.answer("Доступ не активен. Оформите абонемент.")
        return
    
    text = (
        "📊 *Ваш прогресс*\n\n"
        "Здесь вы можете отслеживать свои результаты:\n\n"
        "• 📈 График веса\n"
        "• 📏 Замеры тела\n"
        "• 🏆 Достижения\n"
        "• 📸 Фото прогресса"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Добавить вес", callback_data="progress_add_weight")
    builder.button(text="📏 Добавить замеры", callback_data="progress_add_measurements")
    builder.button(text="🏆 Мои достижения", callback_data="progress_achievements")
    builder.button(text="📊 Статистика", callback_data="progress_stats")
    builder.button(text="◀️ Назад", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await callback.answer()

# Добавление веса
@router.callback_query(F.data == "progress_add_weight")
async def add_weight_start(callback: CallbackQuery, state: FSMContext):
    last_weight = await get_last_weight(callback.from_user.id)
    if last_weight:
        weight, date = last_weight
        await callback.message.answer(f"📈 Последний вес: {weight} кг ({datetime.datetime.fromisoformat(date).strftime('%d.%m.%Y')})\n\nВведите текущий вес (кг):")
    else:
        await callback.message.answer("📈 Введите ваш текущий вес (кг):")
    
    await state.set_state(ProgressState.waiting_for_weight)
    await callback.answer()

# Добавление замеров (без веса)
@router.callback_query(F.data == "progress_add_measurements")
async def add_measurements_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📏 Введите объем груди (см, или напишите 'пропустить'):")
    await state.set_state(ProgressState.waiting_for_chest)
    await callback.answer()

# Обработка веса
@router.message(ProgressState.waiting_for_weight, F.text)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(',', '.'))
        if 30 <= weight <= 200:
            await state.update_data(weight=weight)
            await message.answer("💪 Введите объем груди (см, или напишите 'пропустить'):")
            await state.set_state(ProgressState.waiting_for_chest)
        else:
            await message.answer("Пожалуйста, введите корректный вес (30-200 кг):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 75.5):")

# Обработка груди
@router.message(ProgressState.waiting_for_chest, F.text)
async def process_chest(message: Message, state: FSMContext):
    if message.text.lower() in ['пропустить', 'нет', 'skip', '-', '']:
        await state.update_data(chest=None)
    else:
        try:
            chest = float(message.text.replace(',', '.'))
            await state.update_data(chest=chest)
        except ValueError:
            await message.answer("Пожалуйста, введите число или 'пропустить':")
            return
    
    await message.answer("📏 Введите объем талии (см, или напишите 'пропустить'):")
    await state.set_state(ProgressState.waiting_for_waist)

# Обработка талии
@router.message(ProgressState.waiting_for_waist, F.text)
async def process_waist(message: Message, state: FSMContext):
    if message.text.lower() in ['пропустить', 'нет', 'skip', '-', '']:
        await state.update_data(waist=None)
    else:
        try:
            waist = float(message.text.replace(',', '.'))
            await state.update_data(waist=waist)
        except ValueError:
            await message.answer("Пожалуйста, введите число или 'пропустить':")
            return
    
    await message.answer("🦵 Введите объем бедер (см, или напишите 'пропустить'):")
    await state.set_state(ProgressState.waiting_for_hips)

# Обработка бедер
@router.message(ProgressState.waiting_for_hips, F.text)
async def process_hips(message: Message, state: FSMContext):
    if message.text.lower() in ['пропустить', 'нет', 'skip', '-', '']:
        await state.update_data(hips=None)
    else:
        try:
            hips = float(message.text.replace(',', '.'))
            await state.update_data(hips=hips)
        except ValueError:
            await message.answer("Пожалуйста, введите число или 'пропустить':")
            return
    
    await message.answer("💪 Введите объем руки (см, или напишите 'пропустить'):")
    await state.set_state(ProgressState.waiting_for_arms)

# Обработка рук
@router.message(ProgressState.waiting_for_arms, F.text)
async def process_arms(message: Message, state: FSMContext):
    if message.text.lower() in ['пропустить', 'нет', 'skip', '-', '']:
        await state.update_data(arms=None)
    else:
        try:
            arms = float(message.text.replace(',', '.'))
            await state.update_data(arms=arms)
        except ValueError:
            await message.answer("Пожалуйста, введите число или 'пропустить':")
            return
    
    await message.answer("📝 Добавьте заметки (или напишите 'нет'):")
    await state.set_state(ProgressState.waiting_for_notes)

# Обработка заметок и сохранение всех данных
@router.message(ProgressState.waiting_for_notes, F.text)
async def process_notes(message: Message, state: FSMContext):
    notes = message.text if message.text.lower() != 'нет' else ''
    await state.update_data(notes=notes)
    
    data = await state.get_data()
    today = datetime.datetime.now().isoformat()
    
    # Сохраняем данные
    await add_progress_data(
        message.from_user.id,
        today,
        data.get('weight'),
        data.get('chest'),
        data.get('waist'),
        data.get('hips'),
        data.get('arms'),
        notes
    )
    
    # Формируем сообщение о сохраненных данных
    response_text = "✅ *Данные сохранены!*\n\n"
    
    if data.get('weight'):
        response_text += f"📈 Вес: {data['weight']} кг\n"
    if data.get('chest'):
        response_text += f"📏 Грудь: {data['chest']} см\n"
    if data.get('waist'):
        response_text += f"📏 Талия: {data['waist']} см\n"
    if data.get('hips'):
        response_text += f"📏 Бедра: {data['hips']} см\n"
    if data.get('arms'):
        response_text += f"📏 Руки: {data['arms']} см\n"
    if notes:
        response_text += f"📝 Заметки: {notes}\n"
    
    response_text += "\n📊 Вы можете посмотреть статистику в разделе «Прогресс»"
    
    await message.answer(response_text)
    await state.clear()

# Статистика и графики
@router.callback_query(F.data == "progress_stats")
async def show_progress_stats(callback: CallbackQuery):
    progress_data = await get_progress_data(callback.from_user.id, 30)
    
    if not progress_data:
        await callback.answer("📊 Нет данных для построения графика. Добавьте хотя бы одну запись веса.")
        return
    
    # Создаем график веса
    dates = []
    weights = []
    
    for data in reversed(progress_data):  # В хронологическом порядке
        date_str, weight, chest, waist, hips, arms, notes = data
        if weight:
            dates.append(datetime.datetime.fromisoformat(date_str).strftime('%d.%m'))
            weights.append(weight)
    
    if len(weights) < 2:
        await callback.answer("📈 Нужно хотя бы 2 записи веса для построения графика.")
        return
    
    try:
        # Создаем график
        plt.figure(figsize=(10, 6))
        plt.plot(dates, weights, marker='o', linewidth=2, markersize=6)
        plt.title('📈 Динамика веса', fontsize=14, fontweight='bold')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Вес (кг)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Сохраняем в buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Отправляем график
        await callback.message.answer_photo(
            photo=buf, 
            caption="📊 Ваша динамика веса\n\nДобавляйте вес регулярно для точного отслеживания прогресса! 💪"
        )
        
    except Exception as e:
        print(f"Ошибка при создании графика: {e}")
        # Текстовая версия если график не получился
        text = "📊 *Статистика веса:*\n\n"
        text += f"• Текущий вес: {weights[-1]} кг\n"
        if len(weights) > 1:
            text += f"• Изменение: {weights[-1] - weights[0]:.1f} кг\n"
        text += f"• Записей: {len(weights)}"
        await callback.message.answer(text)
    
    await callback.answer()

# Достижения
@router.callback_query(F.data == "progress_achievements")
async def show_achievements(callback: CallbackQuery):
    achievements = await get_achievements(callback.from_user.id)
    
    if not achievements:
        await callback.answer("У вас пока нет достижений. Продолжайте работать! 💪")
        return
    
    text = "🏆 *Ваши достижения:*\n\n"
    for achievement in achievements:
        achievement_type, achievement_date, description = achievement
        text += f"• {description}\n"
        text += f"  📅 {datetime.datetime.fromisoformat(achievement_date).strftime('%d.%m.%Y')}\n\n"
    
    await callback.message.answer(text)
    await callback.answer()

# Проверка достижений
async def check_weight_achievements(user_id, current_weight):
    progress_data = await get_progress_data(user_id, 30)
    
    # Достижение за регулярность
    weight_records = [data for data in progress_data if data[1] is not None]
    if len(weight_records) >= 7:
        await add_achievement(user_id, "consistency", "7 дней подряд вносил данные веса! 🏆")
    
    # Достижение за прогресс
    if len(weight_records) >= 2:
        first_weight = weight_records[-1][1]
        last_weight = weight_records[0][1]
        difference = last_weight - first_weight
        
        if difference < -2:  # Похудение на 2+ кг
            await add_achievement(user_id, "weight_loss", f"Похудел на {abs(difference):.1f} кг! 💪")
        elif difference > 2:  # Набор массы на 2+ кг
            await add_achievement(user_id, "weight_gain", f"Набрал {difference:.1f} кг мышечной массы! 🏋️")