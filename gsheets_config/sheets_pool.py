# gym_trainer_bot/config/sheets_pool.py

# ПУЛ предварительно созданных таблиц
# ЗАМЕНИ эти ID на реальные ID твоих таблиц
SHEETS_POOL = [
    {
        'id': '1Bq7Phvupy-p7pm-jFppj2CRqjpG-GDjf',  # Замени на реальный ID таблицы "Клиент 1"
        'url': 'https://docs.google.com/spreadsheets/d/1Bq7Phvupy-p7pm-jFppj2CRqjpG-GDjf/edit?gid=833157682#gid=833157682',
        'assigned_to': None,  # Будет содержать user_id когда таблицу назначат
        'original_name': 'Тренировки - Клиент 1'
    },
    {
        'id': '1NLEsNdOYz_T_fxJMYBsOq5cza9v1ULzK',  # Замени на реальный ID таблицы "Клиент 2" 
        'url': 'https://docs.google.com/spreadsheets/d/1NLEsNdOYz_T_fxJMYBsOq5cza9v1ULzK/edit?gid=833157682#gid=833157682',
        'assigned_to': None,
        'original_name': 'Тренировки - Клиент 2'
    },
    {
        'id': '1PJeVBXxcky06KbkMKNyKdn4eIJaCAAIw',  # Замени на реальный ID таблицы "Клиент 3"
        'url': 'https://docs.google.com/spreadsheets/d/1PJeVBXxcky06KbkMKNyKdn4eIJaCAAIw/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 3'
    },
    {
        'id': '1dY0gTtF4PGgamgqDkniLivCe-uaGln2A',  # Замени на реальный ID таблицы "Клиент 4"
        'url': 'https://docs.google.com/spreadsheets/d/1dY0gTtF4PGgamgqDkniLivCe-uaGln2A/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 4'
    },
    {
        'id': '1Cpgean48DW2epFal5EpNtSHmfJ5J1CdA',  # Замени на реальный ID таблицы "Клиент 5"
        'url': 'https://docs.google.com/spreadsheets/d/1Cpgean48DW2epFal5EpNtSHmfJ5J1CdA/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 5'
    },
    {
        'id': '15jfWHG0C2GkxPJh4qZbRMoLrU-ijIske',  # Замени на реальный ID таблицы "Клиент 6"
        'url': 'https://docs.google.com/spreadsheets/d/15jfWHG0C2GkxPJh4qZbRMoLrU-ijIske/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 6'
    },
    {
        'id': '16lc6s_XtVZV0XCB_8byVtV_r_T2KGr0M',  # Замени на реальный ID таблицы "Клиент 7"
        'url': 'https://docs.google.com/spreadsheets/d/16lc6s_XtVZV0XCB_8byVtV_r_T2KGr0M/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 7'
    },
    {
        'id': '1yu9MdvPRBFOcrChJsDKma1fRB9bIoyKg',  # Замени на реальный ID таблицы "Клиент 8"
        'url': 'https://docs.google.com/spreadsheets/d/1yu9MdvPRBFOcrChJsDKma1fRB9bIoyKg/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 8'
    },
    {
        'id': '1yNrm1ynzY4o7xcUMJKhFBBAvLsolE8r3',  # Замени на реальный ID таблицы "Клиент 9"
        'url': 'https://docs.google.com/spreadsheets/d/1yNrm1ynzY4o7xcUMJKhFBBAvLsolE8r3/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 9'
    },
    {
        'id': '11y4GE1D0HO3amrjJ12P7NT9IQzmWaj8N',  # Замени на реальный ID таблицы "Клиент 10"
        'url': 'https://docs.google.com/spreadsheets/d/11y4GE1D0HO3amrjJ12P7NT9IQzmWaj8N/edit?gid=833157682#gid=833157682',
        'assigned_to': None, 
        'original_name': 'Тренировки - Клиент 10'
    },
    # ... добавь остальные 7 таблиц
]

# Резервная таблица если пул закончится
BACKUP_SHEET = {
    'id': 'backup_table_id_here',  # Создай одну резервную таблицу
    'url': 'https://docs.google.com/spreadsheets/d/backup_table_id_here/edit',
    'original_name': 'Тренировки - Резервная'
}