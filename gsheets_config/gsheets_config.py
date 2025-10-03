# gym_trainer_bot/gsheets_config/gsheets_config.py

import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# ВСЕ необходимые scopes для работы с Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',           # Полный доступ к Sheets
    'https://www.googleapis.com/auth/drive',                  # Полный доступ к Drive  
    'https://www.googleapis.com/auth/drive.file',             # Доступ к файлам созданным через приложение
    'https://www.googleapis.com/auth/drive.appdata',          # Доступ к данным приложения
]

CREDENTIALS_FILE = "credentials.json"

def get_gsheets_client():
    """Создает и возвращает клиент Google Sheets"""
    try:
        # Проверяем что файл с credentials существует
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"❌ Файл {CREDENTIALS_FILE} не найден!")
            print("📁 Текущая директория:", os.getcwd())
            print("📁 Содержимое директории:", os.listdir('.'))
            return None
        
        print(f"🔑 Используем scopes: {SCOPES}")
        
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        print("✅ Google Sheets клиент успешно авторизован")
        return client
    except Exception as e:
        print(f"❌ Ошибка инициализации Google Sheets: {e}")
        return None

def get_spreadsheet(spreadsheet_id: str):
    """Возвращает объект таблицы по ID"""
    try:
        client = get_gsheets_client()
        if client:
            spreadsheet = client.open_by_key(spreadsheet_id)
            print(f"✅ Таблица {spreadsheet_id} успешно открыта")
            return spreadsheet
        return None
    except Exception as e:
        print(f"❌ Ошибка открытия таблицы {spreadsheet_id}: {e}")
        return None