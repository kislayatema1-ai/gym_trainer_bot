# gym_trainer_bot/services/gsheets_client_service.py

import json
import os
from datetime import datetime
from gsheets_config.sheets_pool import SHEETS_POOL

class GoogleSheetsClientService:
    def __init__(self):
        self.storage_file = "user_sheets.json"
        self.used_sheets = self._load_used_sheets()
        print(f"✅ Сервис инициализирован. Занято таблиц: {len(self.used_sheets)}")
    
    def _load_used_sheets(self):
        """Загружает данные о занятых таблицах из файла"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
        return {}
    
    def _save_used_sheets(self):
        """Сохраняет данные о занятых таблицах в файл"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.used_sheets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
    
    def _get_available_sheet(self):
        """Находит свободную таблицу из пула"""
        used_ids = {data['spreadsheet_id'] for data in self.used_sheets.values()}
        
        for sheet_info in SHEETS_POOL:
            if sheet_info['id'] not in used_ids:
                return sheet_info
        return None
    
    async def create_client_spreadsheet(self, user_id: int, username: str, full_name: str):
        """Назначает таблицу пользователю и сохраняет данные"""
        try:
            print(f"🔄 Назначаем таблицу для {user_id} ({full_name})")
            
            # Проверяем нет ли уже таблицы у пользователя
            if str(user_id) in self.used_sheets:
                print("⚠️ У пользователя уже есть таблица")
                return self.used_sheets[str(user_id)]
            
            # Находим свободную таблицу
            sheet_info = self._get_available_sheet()
            
            if not sheet_info:
                print("❌ Нет свободных таблиц в пуле")
                return None
            
            # Создаем запись
            result = {
                'spreadsheet_id': sheet_info['id'],
                'spreadsheet_url': sheet_info['url'],
                'user_id': user_id,
                'username': username,
                'full_name': full_name,
                'assigned_name': f"Тренировки - {full_name}",
                'original_name': sheet_info['original_name'],
                'assigned_at': datetime.now().strftime("%d.%m.%Y %H:%M"),
                'note': '💡 Откройте ссылку и начинайте вносить данные тренировок!'
            }
            
            # Сохраняем в память и в файл
            self.used_sheets[str(user_id)] = result
            self._save_used_sheets()
            
            print(f"✅ Таблица назначена и сохранена: {sheet_info['url']}")
            return result
            
        except Exception as e:
            print(f"❌ Ошибка назначения таблицы: {e}")
            return None
    
    async def get_client_sheet(self, user_id: int):
        """Получает информацию о таблице клиента"""
        return self.used_sheets.get(str(user_id))
    
    def get_all_client_sheets(self):
        """Возвращает все занятые таблицы (для тренера)"""
        return self.used_sheets
    
    def get_pool_status(self):
        """Возвращает статус пула таблиц"""
        total = len(SHEETS_POOL)
        used = len(self.used_sheets)
        free = total - used
        
        status = {
            'total': total,
            'used': used,
            'free': free,
            'clients': []
        }
        
        for user_id, sheet_info in self.used_sheets.items():
            status['clients'].append({
                'user_id': user_id,
                'username': sheet_info.get('username', ''),
                'full_name': sheet_info.get('full_name', ''),
                'assigned_at': sheet_info.get('assigned_at', ''),
                'spreadsheet_url': sheet_info['spreadsheet_url']
            })
        
        return status

# Глобальный экземпляр
gsheets_client_service = GoogleSheetsClientService()