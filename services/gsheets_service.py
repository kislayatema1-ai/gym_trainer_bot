# gym_trainer_bot/services/gsheets_service.py

import gspread
from gsheets_config.gsheets_config import get_spreadsheet
from datetime import datetime

class GoogleSheetsService:
    def __init__(self):
        self.spreadsheet = get_spreadsheet()
        self._setup_sheets()
    
    def _setup_sheets(self):
        """Настраивает листы если их нет"""
        if not self.spreadsheet:
            return
        
        try:
            # Пробуем получить лист с клиентами
            self.spreadsheet.worksheet("Клиенты")
        except gspread.WorksheetNotFound:
            # Создаем лист с клиентами
            clients_sheet = self.spreadsheet.add_worksheet("Клиенты", 1000, 10)
            clients_sheet.append_row([
                "user_id", "username", "full_name", "status", 
                "registration_date", "last_active", "trainer_notes"
            ])
        
        try:
            # Пробуем получить лист с тренировками
            self.spreadsheet.worksheet("Тренировки")
        except gspread.WorksheetNotFound:
            # Создаем лист с тренировками
            workouts_sheet = self.spreadsheet.add_worksheet("Тренировки", 1000, 15)
            workouts_sheet.append_row([
                "user_id", "exercise_name", "day", "order", "sets_planned",
                "reps_planned", "weight_planned", "notes", "date_assigned",
                "date_completed", "sets_actual", "reps_actual", "weight_actual",
                "completed_notes", "rating"
            ])
    
    async def register_client(self, user_id: int, username: str, full_name: str):
        """Регистрирует нового клиента"""
        try:
            sheet = self.spreadsheet.worksheet("Клиенты")
            
            # Проверяем нет ли уже клиента
            existing = sheet.find(str(user_id), in_column=1)
            if existing:
                return True
            
            # Добавляем нового клиента
            sheet.append_row([
                str(user_id),
                username or "",
                full_name or "",
                "active",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ""  # trainer_notes
            ])
            return True
        except Exception as e:
            print(f"Ошибка регистрации клиента: {e}")
            return False
    
    async def create_workout_plan(self, user_id: int, workouts: list):
        """Создает план тренировок для клиента"""
        try:
            sheet = self.spreadsheet.worksheet("Тренировки")
            
            for i, workout in enumerate(workouts):
                sheet.append_row([
                    str(user_id),
                    workout.get("exercise_name", ""),
                    workout.get("day", 1),
                    i + 1,
                    workout.get("sets", 0),
                    workout.get("reps", 0),
                    workout.get("weight", 0),
                    workout.get("notes", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "",  # date_completed
                    "",  # sets_actual
                    "",  # reps_actual
                    "",  # weight_actual
                    "",  # completed_notes
                    ""   # rating
                ])
            return True
        except Exception as e:
            print(f"Ошибка создания плана тренировок: {e}")
            return False
    
    async def get_client_workouts(self, user_id: int):
        """Получает тренировки клиента"""
        try:
            sheet = self.spreadsheet.worksheet("Тренировки")
            records = sheet.get_all_records()
            
            client_workouts = []
            for record in records:
                if record.get("user_id") == str(user_id):
                    client_workouts.append(record)
            
            return client_workouts
        except Exception as e:
            print(f"Ошибка получения тренировок: {e}")
            return []
    
    async def update_workout_result(self, user_id: int, exercise_name: str, results: dict):
        """Обновляет результаты тренировки"""
        try:
            sheet = self.spreadsheet.worksheet("Тренировки")
            records = sheet.get_all_records()
            
            for i, record in enumerate(records):
                if (record.get("user_id") == str(user_id) and 
                    record.get("exercise_name") == exercise_name and 
                    not record.get("date_completed")):
                    
                    # Обновляем строку (i+2 потому что первая строка - заголовки)
                    row_num = i + 2
                    sheet.update_cell(row_num, 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # date_completed
                    sheet.update_cell(row_num, 11, results.get("sets"))  # sets_actual
                    sheet.update_cell(row_num, 12, results.get("reps"))  # reps_actual
                    sheet.update_cell(row_num, 13, results.get("weight"))  # weight_actual
                    sheet.update_cell(row_num, 14, results.get("notes", ""))  # completed_notes
                    
                    return True
            return False
        except Exception as e:
            print(f"Ошибка обновления тренировки: {e}")
            return False

# Глобальный экземпляр сервиса
gsheets_service = GoogleSheetsService()