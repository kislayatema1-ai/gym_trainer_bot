import aiosqlite
import datetime
from config import config

# Путь к файлу базы данных
DB_PATH = "database.db"

# Функция для ПЕРВОНАЧАЛЬНОГО создания таблиц
async def create_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                access_until DATE DEFAULT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_onboarding (
                user_id INTEGER PRIMARY KEY,
                received_pdf INTEGER DEFAULT 0,
                used_pdf INTEGER DEFAULT 0,
                wants_nutrition_plan INTEGER DEFAULT 0,
                goal TEXT,
                allergies INTEGER DEFAULT 0,
                allergies_details TEXT,
                training_frequency TEXT,
                height INTEGER,
                weight REAL,
                age INTEGER,
                wants_personal_plan INTEGER DEFAULT 0,
                last_question_date TEXT,
                next_question_date TEXT,
                payment_screenshot_id TEXT,
                payment_status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS training_programs (
                program_id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_name TEXT NOT NULL,
                program_file_id TEXT,
                program_description TEXT,
                created_date TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_training_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                video_file_id TEXT,
                comment TEXT,
                report_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                report_date TEXT,
                meal_breakfast TEXT,
                meal_lunch TEXT,
                meal_dinner TEXT,
                meal_snacks TEXT,
                water_intake INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS exercise_videos_yt (
                video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_name TEXT NOT NULL,
                youtube_url TEXT NOT NULL,
                description TEXT,
                category TEXT,
                created_date TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_calories (
                user_id INTEGER PRIMARY KEY,
                calories_norm INTEGER,
                protein_norm INTEGER,
                fat_norm INTEGER,
                carbs_norm INTEGER,
                last_updated TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS calorie_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                age INTEGER,
                weight REAL,
                height REAL,
                gender TEXT,
                activity_level TEXT,
                goal TEXT,
                status TEXT DEFAULT 'pending',
                created_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS exercise_videos (
                video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_name TEXT NOT NULL,
                video_file_id TEXT,
                description TEXT,
                category TEXT,
                created_date TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS exercise_literature (
                doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_id TEXT,
                description TEXT,
                category TEXT,
                created_date TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_training_sheets (
                user_id INTEGER PRIMARY KEY,
                sheet_url TEXT NOT NULL,
                created_date TEXT,
                last_updated TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT NOT NULL,
                weight REAL,
                chest REAL,
                waist REAL,
                hips REAL,
                arms REAL,
                notes TEXT,
                photo_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_type TEXT NOT NULL,
                achievement_date TEXT,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        # Таблица платежей на проверке
        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                screenshot_id TEXT,
                date TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                screenshot_id TEXT,
                product_type TEXT DEFAULT 'full',  -- 'nutrition' или 'full'
                date TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq_categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                category_description TEXT,
                created_date TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS faq_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_date TEXT,
                FOREIGN KEY (category_id) REFERENCES faq_categories (category_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_onboarding (
                user_id INTEGER PRIMARY KEY,
                received_pdf INTEGER DEFAULT 0,
                used_pdf INTEGER DEFAULT 0,
                wants_nutrition_plan INTEGER DEFAULT 0,
                goal TEXT,
                allergies TEXT,
                training_frequency TEXT,
                wants_personal_plan INTEGER DEFAULT 0,
                last_question_date TEXT,
                next_question_date TEXT,
                payment_screenshot_id TEXT,
                payment_status TEXT DEFAULT 'pending',
                -- Новые поля для полной анкеты
                experience TEXT,
                equipment TEXT,
                schedule TEXT,
                food_preferences TEXT,
                food_allergies TEXT,
                age INTEGER,
                height INTEGER,
                weight REAL,
                activity_level TEXT,
                sleep TEXT,
                stress_level TEXT,
                training_days INTEGER,
                training_time INTEGER,
                favorite_foods TEXT,
                disliked_foods TEXT,
                water_intake TEXT,
                supplements TEXT,
                health_issues TEXT,
                motivation TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS user_onboarding (
                user_id INTEGER PRIMARY KEY,
                received_pdf INTEGER DEFAULT 0,
                used_pdf INTEGER DEFAULT 0,
                wants_nutrition_plan INTEGER DEFAULT 0,
                goal TEXT,
                allergies TEXT,
                training_frequency TEXT,
                wants_personal_plan INTEGER DEFAULT 0,
                last_question_date TEXT,
                next_question_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT NOT NULL,
                message_type TEXT,
                status TEXT DEFAULT 'new',
                created_date TEXT,
                response_text TEXT,
                response_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        print("Database tables are ready!")
        await db.commit()

async def update_onboarding_table():
    """Добавляет новые поля в таблицу user_onboarding если их нет"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Список новых полей для анкеты
        columns_to_add = [
            'experience', 'equipment', 'schedule', 'food_preferences', 
            'food_allergies', 'age', 'height', 'weight', 'activity_level',
            'sleep', 'stress_level', 'training_days', 'training_time',
            'favorite_foods', 'disliked_foods', 'water_intake', 'supplements',
            'health_issues', 'motivation', 'daily_steps'  # ДОБАВЛЯЕМ daily_steps
        ]
        
        for column in columns_to_add:
            try:
                await db.execute(f"ALTER TABLE user_onboarding ADD COLUMN {column} TEXT")
                print(f"✓ Добавлено поле: {column}")
            except aiosqlite.OperationalError:
                print(f"✓ Поле уже существует: {column}")
                pass
        
        await db.commit()

async def get_full_onboarding_data(user_id):
    """Получает все данные анкеты в виде словаря"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM user_onboarding WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = await cursor.fetchone()
            
            if result:
                return dict(zip(columns, result))
            return {}

# Функция для добавления нового пользователя или обновления его данных
async def add_user(user_id, username, full_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()

# Функции для onboarding
async def init_user_onboarding(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO user_onboarding (user_id) VALUES (?)",
            (user_id,)
        )
        await db.commit()

async def save_training_sheet_url(user_id, sheet_url):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO user_training_sheets 
            (user_id, sheet_url, created_date, last_updated) 
            VALUES (?, ?, ?, ?)""",
            (user_id, sheet_url, created_date, created_date)
        )
        await db.commit()

async def get_training_sheet_url(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT sheet_url FROM user_training_sheets WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def update_onboarding_data(user_id, **kwargs):
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    values = list(kwargs.values())
    values.append(user_id)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE user_onboarding SET {set_clause} WHERE user_id = ?",
            values
        )
        await db.commit()

async def get_onboarding_data(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT received_pdf, used_pdf, wants_nutrition_plan, goal, allergies, training_frequency, wants_personal_plan, next_question_date FROM user_onboarding WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result

async def get_users_for_followup():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM user_onboarding WHERE received_pdf = 1 AND used_pdf = 0 AND next_question_date <= datetime('now')"
        ) as cursor:
            results = await cursor.fetchall()
            return [result[0] for result in results]

# Функция для проверки, есть ли у пользователя активный доступ
async def check_user_access(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT access_until FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            if result and result[0]:
                access_date = datetime.datetime.strptime(result[0], '%Y-%m-%d').date()
                return access_date >= datetime.date.today()
            return False

# FAQ функции
async def add_faq_category(name, description):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO faq_categories (category_name, category_description, created_date) VALUES (?, ?, ?)",
            (name, description, created_date)
        )
        await db.commit()

async def add_faq_item(category_id, question, answer):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO faq_items (category_id, question, answer, created_date) VALUES (?, ?, ?, ?)",
            (category_id, question, answer, created_date)
        )
        await db.commit()

async def get_faq_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT category_id, category_name, category_description FROM faq_categories ORDER BY category_name"
        ) as cursor:
            results = await cursor.fetchall()
            return results

async def get_faq_items(category_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category_id:
            async with db.execute(
                """SELECT f.item_id, f.question, f.answer, c.category_name 
                FROM faq_items f 
                JOIN faq_categories c ON f.category_id = c.category_id 
                WHERE f.category_id = ? 
                ORDER BY f.question""",
                (category_id,)
            ) as cursor:
                results = await cursor.fetchall()
                return results
        else:
            async with db.execute(
                """SELECT f.item_id, f.question, f.answer, c.category_name 
                FROM faq_items f 
                JOIN faq_categories c ON f.category_id = c.category_id 
                ORDER BY c.category_name, f.question"""
            ) as cursor:
                results = await cursor.fetchall()
                return results

# Функции поддержки
async def add_support_message(user_id, message_text, message_type="general"):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO support_messages (user_id, message_text, message_type, created_date) VALUES (?, ?, ?, ?)",
            (user_id, message_text, message_type, created_date)
        )
        await db.commit()

async def get_support_messages(status="new"):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT s.message_id, s.user_id, u.username, u.full_name, s.message_text, s.message_type, s.created_date 
            FROM support_messages s 
            JOIN users u ON s.user_id = u.user_id 
            WHERE s.status = ? 
            ORDER BY s.created_date""",
            (status,)
        ) as cursor:
            results = await cursor.fetchall()
            return results

async def update_support_message(message_id, response_text, status="answered"):
    response_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE support_messages SET response_text = ?, response_date = ?, status = ? WHERE message_id = ?",
            (response_text, response_date, status, message_id)
        )
        await db.commit()

# Сохранение отчета о питании
async def add_nutrition_report(user_id, breakfast, lunch, dinner, snacks, water, notes):
    report_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO nutrition_reports 
            (user_id, report_date, meal_breakfast, meal_lunch, meal_dinner, meal_snacks, water_intake, notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, report_date, breakfast, lunch, dinner, snacks, water, notes)
        )
        await db.commit()

# Добавление данных прогресса
async def add_progress_data(user_id, date, weight=None, chest=None, waist=None, hips=None, arms=None, notes=None, photo_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO user_progress 
            (user_id, date, weight, chest, waist, hips, arms, notes, photo_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, date, weight, chest, waist, hips, arms, notes, photo_id)
        )
        await db.commit()

# Получение данных прогресса
async def get_progress_data(user_id, limit=10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT date, weight, chest, waist, hips, arms, notes FROM user_progress WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Получение последнего веса
async def get_last_weight(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT weight, date FROM user_progress WHERE user_id = ? AND weight IS NOT NULL ORDER BY date DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result

# Добавление достижения
async def add_achievement(user_id, achievement_type, description):
    achievement_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_achievements (user_id, achievement_type, achievement_date, description) VALUES (?, ?, ?, ?)",
            (user_id, achievement_type, description, achievement_date)
        )
        await db.commit()

# Получение достижений пользователя
async def get_achievements(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT achievement_type, achievement_date, description FROM user_achievements WHERE user_id = ? ORDER BY achievement_date DESC",
            (user_id,)
        ) as cursor:
            results = await cursor.fetchall()
            return results

async def get_last_progress_date(user_id):
    """Получаем дату последней записи прогресса пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT date FROM user_progress WHERE user_id = ? ORDER BY date DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

async def get_users_with_expiring_access(days_before=3):
    """Получаем пользователей с истекающим доступом"""
    target_date = (datetime.date.today() + datetime.timedelta(days=days_before)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, access_until FROM users WHERE access_until <= ? AND access_until >= ?",
            (target_date, datetime.date.today().isoformat())
        ) as cursor:
            results = await cursor.fetchall()
            return results

async def get_users_with_active_access():
    """Получаем всех пользователей с активным доступом"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, access_until FROM users WHERE access_until >= date('now')"
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Функции для YouTube видео
async def add_youtube_video(name, url, description, category):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO exercise_videos_yt (exercise_name, youtube_url, description, category, created_date) VALUES (?, ?, ?, ?, ?)",
            (name, url, description, category, created_date)
        )
        await db.commit()

async def get_youtube_videos(category=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            async with db.execute(
                "SELECT video_id, exercise_name, youtube_url, description FROM exercise_videos_yt WHERE category = ? ORDER BY exercise_name",
                (category,)
            ) as cursor:
                results = await cursor.fetchall()
                return results
        else:
            async with db.execute(
                "SELECT video_id, exercise_name, youtube_url, description, category FROM exercise_videos_yt ORDER BY category, exercise_name"
            ) as cursor:
                results = await cursor.fetchall()
                return results

# Получение отчетов о питании за последние дни
async def get_nutrition_reports(user_id, days=7):
    since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT report_date, meal_breakfast, meal_lunch, meal_dinner, meal_snacks, water_intake, notes FROM nutrition_reports WHERE user_id = ? AND report_date >= ? ORDER BY report_date DESC",
            (user_id, since_date)
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Добавление видео упражнения
async def add_exercise_video(name, file_id, description, category):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO exercise_videos (exercise_name, video_file_id, description, category, created_date) VALUES (?, ?, ?, ?, ?)",
            (name, file_id, description, category, created_date)
        )
        await db.commit()

# Получение всех пользователей
async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, access_until FROM users ORDER BY user_id"
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Получение статистики
async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        # Общее количество пользователей
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
        
        # Активные пользователи
        async with db.execute("SELECT COUNT(*) FROM users WHERE access_until >= date('now')") as cursor:
            active_users = (await cursor.fetchone())[0]
        
        # Платежи на проверке
        async with db.execute("SELECT COUNT(*) FROM payments WHERE status = 'pending'") as cursor:
            pending_payments = (await cursor.fetchone())[0]
        
        # Запросы калорий на проверке
        async with db.execute("SELECT COUNT(*) FROM calorie_requests WHERE status = 'pending'") as cursor:
            pending_calories = (await cursor.fetchone())[0]
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'pending_payments': pending_payments,
            'pending_calories': pending_calories
        }

# Добавление доступа пользователю
async def add_user_access(user_id, days):
    current_access = await get_access_until(user_id)
    if current_access and current_access != "Не активен":
        current_date = datetime.datetime.strptime(current_access, '%Y-%m-%d').date()
        new_access_date = current_date + datetime.timedelta(days=days)
    else:
        new_access_date = datetime.date.today() + datetime.timedelta(days=days)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET access_until = ? WHERE user_id = ?",
            (new_access_date.isoformat(), user_id)
        )
        await db.commit()
    
    return new_access_date.isoformat()

# Получение всех видео упражнений
async def get_exercise_videos(category=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            async with db.execute(
                "SELECT exercise_name, video_file_id, description FROM exercise_videos WHERE category = ? ORDER BY exercise_name",
                (category,)
            ) as cursor:
                results = await cursor.fetchall()
                return results
        else:
            async with db.execute(
                "SELECT exercise_name, video_file_id, description, category FROM exercise_videos ORDER BY category, exercise_name"
            ) as cursor:
                results = await cursor.fetchall()
                return results

# Добавление литературного материала
async def add_exercise_literature(title, file_id, description, category):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO exercise_literature (title, file_id, description, category, created_date) VALUES (?, ?, ?, ?, ?)",
            (title, file_id, description, category, created_date)
        )
        await db.commit()

# Получение литературных материалов
async def get_exercise_literature(category=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category:
            async with db.execute(
                "SELECT title, file_id, description FROM exercise_literature WHERE category = ? ORDER BY title",
                (category,)
            ) as cursor:
                results = await cursor.fetchall()
                return results
        else:
            async with db.execute(
                "SELECT title, file_id, description, category FROM exercise_literature ORDER BY category, title"
            ) as cursor:
                results = await cursor.fetchall()
                return results

# Сохранение норм калорий
async def save_calorie_norms(user_id, calories, protein, fat, carbs):
    last_updated = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO user_calories 
            (user_id, calories_norm, protein_norm, fat_norm, carbs_norm, last_updated) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, calories, protein, fat, carbs, last_updated)
        )
        await db.commit()

# Получение норм калорий
async def get_calorie_norms(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT calories_norm, protein_norm, fat_norm, carbs_norm, last_updated FROM user_calories WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result

# Сохранение запроса на расчет калорий
async def add_calorie_request(user_id, age, weight, height, gender, activity, goal):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO calorie_requests 
            (user_id, age, weight, height, gender, activity_level, goal, created_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, age, weight, height, gender, activity, goal, created_date)
        )
        await db.commit()

# Получение запросов на расчет калорий
async def get_pending_calorie_requests():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT r.request_id, r.user_id, u.full_name, u.username, r.age, r.weight, r.height, 
            r.gender, r.activity_level, r.goal, r.created_date 
            FROM calorie_requests r 
            JOIN users u ON r.user_id = u.user_id 
            WHERE r.status = 'pending' 
            ORDER BY r.created_date DESC"""
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Обновление статуса запроса
async def update_calorie_request_status(request_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE calorie_requests SET status = ? WHERE request_id = ?",
            (status, request_id)
        )
        await db.commit()

# Функция для получения даты, до которой активен доступ
async def get_access_until(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT access_until FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else "Не активен"

# Проверяем, существует ли категория
async def check_category_exists(category_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM faq_categories WHERE category_name = ?",
            (category_name,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] > 0

# Обновляем функцию добавления категории
async def add_faq_category(name, description):
    # Проверяем, не существует ли уже такая категория
    if await check_category_exists(name):
        print(f"Категория '{name}' уже существует, пропускаем добавление.")
        return
    
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO faq_categories (category_name, category_description, created_date) VALUES (?, ?, ?)",
            (name, description, created_date)
        )
        await db.commit()

# Добавляем программу тренировок
async def add_training_program(name, file_id, description):
    created_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        # Делаем все старые программы неактивными
        await db.execute("UPDATE training_programs SET is_active = 0")
        # Добавляем новую активную программу
        await db.execute(
            "INSERT INTO training_programs (program_name, program_file_id, program_description, created_date) VALUES (?, ?, ?, ?)",
            (name, file_id, description, created_date)
        )
        await db.commit()

# Получаем активную программу
async def get_active_training_program():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT program_id, program_name, program_file_id, program_description, created_date FROM training_programs WHERE is_active = 1 ORDER BY program_id DESC LIMIT 1"
        ) as cursor:
            result = await cursor.fetchone()
            return result

# Сохраняем отчет о тренировке
async def add_user_training_report(user_id, video_id, comment):
    report_date = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO user_training_reports (user_id, video_file_id, comment, report_date) VALUES (?, ?, ?, ?)",
            (user_id, video_id, comment, report_date)
        )
        await db.commit()

# Удаление пользователя
async def delete_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        # Удаляем все данные пользователя
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM payments WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM user_achievements WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM support_messages WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM calorie_requests WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM user_calories WHERE user_id = ?", (user_id,))
        await db.commit()

# Получение детальной статистики
async def get_detailed_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        # Общая статистика
        stats = {}
        
        # Количество пользователей
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            stats['total_users'] = (await cursor.fetchone())[0]
        
        # Активные пользователи
        async with db.execute("SELECT COUNT(*) FROM users WHERE access_until >= date('now')") as cursor:
            stats['active_users'] = (await cursor.fetchone())[0]
        
        # Новые пользователи за месяц
        async with db.execute("SELECT COUNT(*) FROM users WHERE date(created) >= date('now', '-30 days')") as cursor:
            stats['new_users_30d'] = (await cursor.fetchone())[0]
        
        # Доход за месяц
        async with db.execute("""
            SELECT COUNT(*) as payments_count, COALESCE(SUM(100), 0) as revenue 
            FROM payments 
            WHERE status = 'approved' AND date >= date('now', '-30 days')
        """) as cursor:
            result = await cursor.fetchone()
            stats['recent_payments'] = result[0]
            stats['recent_revenue'] = result[1]
        
        return stats

# Поиск пользователя
async def search_users(search_term):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_id, username, full_name, access_until 
            FROM users 
            WHERE user_id LIKE ? OR username LIKE ? OR full_name LIKE ?
            ORDER BY user_id
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")) as cursor:
            results = await cursor.fetchall()
            return results

# Функция для обновления доступа пользователя (продления)
async def update_user_access(user_id, days_to_add=30):
    new_access_date = datetime.date.today() + datetime.timedelta(days=days_to_add)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET access_until = ? WHERE user_id = ?",
            (new_access_date.isoformat(), user_id)
        )
        await db.commit()
    return new_access_date.isoformat()

# Функция для сохранения платежа в базу (со статусом 'pending')
async def add_payment(user_id, screenshot_id, product_type='full'):
    date_now = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO payments (user_id, screenshot_id, product_type, date) VALUES (?, ?, ?, ?)",
            (user_id, screenshot_id, product_type, date_now)
        )
        await db.commit()

async def get_payment_type(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT product_type FROM payments WHERE user_id = ? ORDER BY date DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

# Функция для обновления статуса платежа (админ подтвердил или отклонил)
async def update_payment_status(user_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE payments SET status = ? WHERE user_id = ? AND status = 'pending'",
            (status, user_id)
        )
        await db.commit()

# Функция для получения всех платежей, ожидающих проверки
async def get_pending_payments():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT p.user_id, u.username, u.full_name, p.screenshot_id, p.date FROM payments p JOIN users u ON p.user_id = u.user_id WHERE p.status = 'pending'"
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Функция для получения пользователей, у которых скоро закончится доступ
async def get_users_with_expiring_access(days_before=3):
    target_date = (datetime.date.today() + datetime.timedelta(days=days_before)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, username, full_name, access_until FROM users WHERE access_until <= ? AND access_until >= ?",
            (target_date, datetime.date.today().isoformat())
        ) as cursor:
            results = await cursor.fetchall()
            return results

# Функция для получения истории платежей пользователя
async def get_payment_history(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT date, status, screenshot_id FROM payments WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        ) as cursor:
            results = await cursor.fetchall()
            return results

async def add_progress_data(user_id, date, weight=None, chest=None, waist=None, hips=None, arms=None, notes=None):
    print(f"DEBUG: Сохранение данных для user_id={user_id}, weight={weight}, chest={chest}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO user_progress 
            (user_id, date, weight, chest, waist, hips, arms, notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, date, weight, chest, waist, hips, arms, notes)
        )
        await db.commit()
    print("DEBUG: Данные сохранены успешно")

async def update_payments_table():
    """Добавляет колонку product_type в таблицу payments если ее нет"""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("ALTER TABLE payments ADD COLUMN product_type TEXT DEFAULT 'full'")
            print("✓ Добавлено поле product_type в таблицу payments")
        except aiosqlite.OperationalError:
            print("✓ Поле product_type уже существует в таблице payments")
            pass
        await db.commit()