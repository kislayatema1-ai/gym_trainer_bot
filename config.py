import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Создаем класс для удобного доступа к конфигурации
class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Преобразуем ID в число
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '@Daglas99')  # ← Добавляем
    ADMIN_CONTACT = os.getenv('ADMIN_CONTACT', '+375291234567')    # ← Добавляем
    ADMIN_EMAIL = "nastik.mil@mail.ru"
    GOOGLE_SHEETS_TEMPLATE_ID = "1ZyzjcbnHcV8nokGX7fooaFWfBEetv98i"
# Создаем экземпляр конфига
config = Config()