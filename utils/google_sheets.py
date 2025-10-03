import gspread
from google.oauth2.service_account import Credentials
from config import config
import time

class GoogleSheetsManager:
    def __init__(self):
        self.credentials_file = "credentials.json"
        self.setup_client()
    
    def setup_client(self):
        """Настройка клиента Google Sheets"""
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
            self.client = gspread.authorize(creds)
            print("✅ Google Sheets клиент настроен")
        except Exception as e:
            print(f"❌ Ошибка настройки Google Sheets: {e}")
            self.client = None
    
    def create_training_spreadsheet(self, user_id, user_name):
        """Создает новую таблицу для пользователя через сервисный аккаунт"""
        try:
            if not self.client:
                print("❌ Клиент Google Sheets не инициализирован")
                return None
            
            # Создаем новую таблицу ЧЕРЕЗ СЕРВИСНЫЙ АККАУНТ
            sheet_name = f"Тренировки {user_name} (ID: {user_id})"
            print(f"🔄 Создаю таблицу: {sheet_name}")
            
            sheet = self.client.create(sheet_name)
            
            # Даем доступ пользователю по email (если указан в конфиге)
            try:
                if hasattr(config, 'ADMIN_EMAIL') and config.ADMIN_EMAIL:
                    sheet.share(config.ADMIN_EMAIL, perm_type='user', role='writer')
                    print(f"✅ Дален доступ тренеру: {config.ADMIN_EMAIL}")
            except Exception as share_error:
                print(f"⚠️ Не удалось дать доступ тренеру: {share_error}")
            
            # Делаем таблицу доступной по ссылке
            sheet.share(None, perm_type='anyone', role='writer')
            print("✅ Таблица доступна по ссылке")
            
            # Ждем немного перед заполнением
            time.sleep(2)
            
            # Заполняем базовую структуру
            worksheet = sheet.sheet1
            worksheet.update('A1', [
                ['День', 'Упражнение', 'Вес', 'Подход 1', 'Подход 2', 'Подход 3', 'Подход 4', 'Дата', 'Примечания'],
                ['ПОНЕДЕЛЬНИК (Грудь, Трицепс)', '', '', '', '', '', '', '', ''],
                ['', '🏋️ Жим штанги лежа', '', '', '', '', '', '', ''],
                ['', '💪 Разводки гантелей', '', '', '', '', '', '', ''],
                ['', '⬇️ Отжимания на брусьях', '', '', '', '', '', '', ''],
                ['', '🔽 Французский жим', '', '', '', '', '', '', ''],
                ['СРЕДА (Спина, Бицепс)', '', '', '', '', '', '', '', ''],
                ['', '📏 Тяга штанги в наклоне', '', '', '', '', '', '', ''],
                ['', '⬆️ Подтягивания', '', '', '', '', '', '', ''],
                ['', '📎 Тяга гантели', '', '', '', '', '', '', ''],
                ['', '💪 Сгибания рук со штангой', '', '', '', '', '', '', ''],
                ['ПЯТНИЦА (Ноги, Плечи)', '', '', '', '', '', '', '', ''],
                ['', '🦵 Приседания со штангой', '', '', '', '', '', '', ''],
                ['', '🏋️ Жим ногами', '', '', '', '', '', '', ''],
                ['', '📏 Подъемы на носки', '', '', '', '', '', '', ''],
                ['', '👐 Жим гантелей сидя', '', '', '', '', '', '', ''],
                ['', '📈 Махи гантелями', '', '', '', '', '', '', '']
            ])
            
            # Настраиваем ширину колонок
            worksheet.format('A1:I1', {'textFormat': {'bold': True}})
            
            print(f"✅ Таблица создана: {sheet.url}")
            return sheet.url
            
        except Exception as e:
            print(f"❌ Ошибка создания таблицы: {e}")
            return None

# Создаем глобальный экземпляр
sheets_manager = GoogleSheetsManager()