# gym_trainer_bot/handlers/training.py

import os
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from services.gsheets_client_service import gsheets_client_service
from keyboards.main_menu import (
    get_main_keyboard, 
    get_training_main_keyboard,   # Главное меню тренировок (без кнопки Назад)
    get_training_back_keyboard    # Меню с кнопкой Назад
)

router = Router()

@router.message(F.text == "🏋️ Тренировки")
async def training_main_handler(message: Message, state: FSMContext):
    """Главное меню тренировок - УРОВЕНЬ 1"""
    await message.answer(
        "💪 *Раздел тренировок*\n\n"
        "Выбери действие:",
        reply_markup=get_training_main_keyboard()  # Без кнопки "Назад"
    )

@router.callback_query(F.data == "training_create_sheet")
async def create_spreadsheet_callback(callback: CallbackQuery):
    """Создает таблицу - УРОВЕНЬ 2"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.full_name
    
    await callback.message.edit_text("🔄 Создаю твою персональную таблицу...")
    
    sheet_info = await gsheets_client_service.create_client_spreadsheet(
        user_id, username, full_name
    )
    
    if sheet_info:
        response = (
            f"🎉 *Твоя персональная таблица готова!*\n\n"
            f"📊 *Таблица тренировок:*\n"
            f"🔗 {sheet_info['spreadsheet_url']}\n\n"
            f"*Что делать дальше:*\n"
            f"1. Открой ссылку выше\n"
            f"2. Начни вносить свои тренировки\n"
            f"3. Сохраняй прогресс после каждой тренировки\n"
            f"4. Тренер будет видеть твои результаты\n\n"
            f"💡 *Совет:* Вноси данные сразу после тренировки!"
        )
    else:
        response = (
            "❌ *К сожалению, сейчас нет свободных таблиц.*\n\n"
            "Пожалуйста, свяжись с тренером для получения доступа."
        )
    
    await callback.message.edit_text(
        response, 
        reply_markup=get_training_back_keyboard()  # С кнопкой "Назад"
    )

@router.callback_query(F.data == "training_my_sheet")
async def my_spreadsheet_callback(callback: CallbackQuery):
    """Показывает таблицу - УРОВЕНЬ 2"""
    user_id = callback.from_user.id
    
    sheet_info = await gsheets_client_service.get_client_sheet(user_id)
    
    if sheet_info:
        response = (
            f"📊 *Твоя таблица тренировок*\n\n"
            f"👤 *Клиент:* {sheet_info.get('full_name', '')}\n"
            f"📅 *Назначена:* {sheet_info.get('assigned_at', '')}\n\n"
            f"🔗 *Ссылка на таблицу:*\n"
            f"{sheet_info['spreadsheet_url']}\n\n"
            f"💡 Просто открой ссылку и вноси свои результаты!"
        )
    else:
        response = (
            "❌ *У тебя еще нет таблицы тренировок.*\n\n"
            "Нажми \"🆕 Создать таблицу\" чтобы получить свою персональную таблицу!"
        )
    
    await callback.message.edit_text(
        response, 
        reply_markup=get_training_back_keyboard()  # С кнопкой "Назад"
    )

@router.callback_query(F.data == "training_progress")
async def progress_callback(callback: CallbackQuery):
    """Показывает прогресс - УРОВЕНЬ 2"""
    user_id = callback.from_user.id
    
    sheet_info = await gsheets_client_service.get_client_sheet(user_id)
    
    if sheet_info:
        response = (
            f"📈 *Твой прогресс*\n\n"
            f"👤 *Клиент:* {sheet_info.get('full_name', '')}\n"
            f"📅 *Таблица создана:* {sheet_info.get('assigned_at', '')}\n\n"
            f"📊 *Твоя таблица тренировок:*\n"
            f"🔗 {sheet_info['spreadsheet_url']}\n\n"
            f"💡 *Что отслеживать:*\n"
            f"• Рост рабочих весов\n"
            f"• Увеличение подходов/повторений\n"
            f"• Общую динамику тренировок\n\n"
            f"Открывай таблицу и анализируй свой прогресс!"
        )
    else:
        response = (
            "📈 *Твой прогресс*\n\n"
            "У тебя еще нет таблицы тренировок для отслеживания прогресса.\n\n"
            "Нажми \"🆕 Создать таблицу\" чтобы начать отслеживать свои результаты!"
        )
    
    await callback.message.edit_text(
        response, 
        reply_markup=get_training_back_keyboard()  # С кнопкой "Назад"
    )

@router.callback_query(F.data == "training_help")
async def instruction_callback(callback: CallbackQuery):
    """Показывает инструкцию - УРОВЕНЬ 2"""
    instruction = (
        "📝 *Инструкция по работе с таблицей:*\n\n"
        "1. *Открой свою таблицу* через кнопку \"📊 Моя таблица\"\n"
        "2. *Вноси данные* после каждой тренировки:\n"
        "   - 📅 *Дата* тренировки\n"
        "   - 🏋️ *Упражнение*\n"
        "   - 🔢 *Подходы* и *повторения*\n"
        "   - ⚖️ *Рабочий вес*\n"
        "   - 💭 *Примечания* (самочувствие, техника)\n\n"
        "3. *Тренер видит* твой прогресс и может корректировать программу\n"
        "4. *Все данные* сохраняются автоматически в Google Sheets\n\n"
        "💡 *Советы:*\n"
        "• Вноси данные сразу после тренировки\n"
        "• Будь честен с результатами\n"
        "• Отмечай свое самочувствие"
    )
    
    await callback.message.edit_text(
        instruction, 
        reply_markup=get_training_back_keyboard()  # С кнопкой "Назад"
    )

@router.callback_query(F.data == "training_back_to_main")
async def back_to_training_main(callback: CallbackQuery):
    """Возврат в главное меню тренировок - из УРОВНЯ 2 в УРОВЕНЬ 1"""
    await callback.message.edit_text(
        "💪 *Раздел тренировок*\n\n"
        "Выбери действие:",
        reply_markup=get_training_main_keyboard()  # Без кнопки "Назад"
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат в главное меню бота - из УРОВНЯ 1"""
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )

# Команда для тренера - просмотр всех клиентов
@router.message(Command("clients"))
async def show_clients(message: Message):
    """Показывает всех клиентов и их таблицы (для тренера)"""
    status = gsheets_client_service.get_pool_status()
    
    response = f"📊 *Статус клиентов*\n\n"
    response += f"• Всего таблиц: {status['total']}\n"
    response += f"• Занято: {status['used']}\n"
    response += f"• Свободно: {status['free']}\n\n"
    
    if status['clients']:
        response += "*Клиенты:*\n"
        for client in status['clients']:
            response += f"👤 {client['full_name']} (@{client['username']})\n"
            response += f"   📅 {client['assigned_at']}\n"
            response += f"   🔗 {client['spreadsheet_url']}\n\n"
    else:
        response += "Пока нет клиентов с таблицами."
    
    await message.answer(response)