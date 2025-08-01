import sqlite3
import os
from flask import g, current_app

def get_db():
    """Получение соединения с базой данных."""
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE_PATH'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Закрытие соединения с базой данных."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Инициализация базы данных и создание таблиц."""
    db = get_db()
    
    # Создание таблицы пациентов с обновленной структурой
    db.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            birth_year INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            attending_doctor TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы медицинских препаратов с обновленной структурой
    db.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            smmn_node_code TEXT NOT NULL,
            section TEXT NOT NULL,
            standardized_mnn TEXT NOT NULL,
            trade_name_vk TEXT NOT NULL,
            standardized_dosage_form TEXT NOT NULL,
            standardized_dosage TEXT NOT NULL,
            characteristic TEXT,
            packaging TEXT NOT NULL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы назначений лекарственных препаратов
    db.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            prescription_date DATE NOT NULL,
            quantity_packs REAL NOT NULL,
            daily_dose REAL,
            treatment_days INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (medicine_id) REFERENCES medicines (medicine_id)
        )
    ''')
    
    # Создание таблицы фактических выдач препаратов
    db.execute('''
        CREATE TABLE IF NOT EXISTS dispensings (
            dispensing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            dispensing_date DATE NOT NULL,
            quantity_packs REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (medicine_id) REFERENCES medicines (medicine_id)
        )
    ''')
    
    # Создание индексов для улучшения производительности при работе с большими объемами данных
    db.execute('CREATE INDEX IF NOT EXISTS idx_patients_fio ON patients (fio)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_patients_diagnosis ON patients (diagnosis)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_patients_doctor ON patients (attending_doctor)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_medicines_mnn ON medicines (standardized_mnn)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_medicines_trade_name ON medicines (trade_name_vk)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_medicines_section ON medicines (section)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_medicine ON prescriptions (patient_id, medicine_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_dispensings_patient_medicine ON dispensings (patient_id, medicine_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_prescriptions_date ON prescriptions (prescription_date)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_dispensings_date ON dispensings (dispensing_date)')
    
    db.commit()

def insert_sample_data():
    """Вставка примерных данных для демонстрации с новым форматом."""
    db = get_db()
    
    # Проверяем, есть ли уже данные
    cursor = db.execute('SELECT COUNT(*) FROM patients')
    if cursor.fetchone()[0] > 0:
        return  # Данные уже есть
    
    # Добавление примерных пациентов согласно новому формату
    patients_data = [
        ('Абаева Татьяна Петровна', 1960, 'K81.1-Хронический холецистит', 'н/д'),
        ('Абаева Татьяна Петровна', 1960, 'E11.7-Инсулиннезависимый сахарный диабет с множественными осложнениями', 'Ачабаева Анна Васильевна'),
        ('Абакумов Александр Викторович', 1963, 'H52.1-Миопия', 'н/д'),
    ]
    
    for patient in patients_data:
        db.execute('''
            INSERT INTO patients (fio, birth_year, diagnosis, attending_doctor)
            VALUES (?, ?, ?, ?)
        ''', patient)
    
    # Добавление примерных медицинских препаратов согласно новому формату
    medicines_data = [
        ('21.20.10.236-000024-1-00114-0000000000000', '1 (а)', 'АГОМЕЛАТИН', 'н/д', 'ТАБЛЕТКИ, ПОКРЫТЫЕ ОБОЛОЧКОЙ', '25 мг', 'н/д', '28', 1307.00),
        ('21.20.10.110-000008-1-00059-0000000000000', '5', 'АДЕМЕТИОНИН', 'н/д', 'ТАБЛЕТКИ, ПОКРЫТЫЕ ОБОЛОЧКОЙ', '500 мг', 'н/д', '20', 1530.00),
        ('21,20,10,110-000008-1-00061-0000000000000', '5', 'АДЕМЕТИОНИН', 'н/д', 'ТАБЛЕТКИ, ПОКРЫТЫЕ ОБОЛОЧКОЙ', '400 мг', 'н/д', '20', 692.00),
    ]
    
    for medicine in medicines_data:
        db.execute('''
            INSERT INTO medicines (smmn_node_code, section, standardized_mnn, trade_name_vk, 
                                   standardized_dosage_form, standardized_dosage, characteristic, 
                                   packaging, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', medicine)
    
    # Добавление примерных назначений
    prescriptions_data = [
        (1, 1, '2024-01-15', 2.0),  # Абаева - АГОМЕЛАТИН
        (2, 2, '2024-01-16', 1.5),  # Абаева - АДЕМЕТИОНИН
        (3, 3, '2024-01-17', 1.0),  # Абакумов - АДЕМЕТИОНИН
    ]
    
    for prescription in prescriptions_data:
        db.execute('''
            INSERT INTO prescriptions (patient_id, medicine_id, prescription_date, quantity_packs)
            VALUES (?, ?, ?, ?)
        ''', prescription)
    
    # Добавление примерных выдач
    dispensings_data = [
        (1, 1, '2024-01-20', 1.0),  # Абаева - АГОМЕЛАТИН (частичная выдача)
        (2, 2, '2024-01-21', 1.5),  # Абаева - АДЕМЕТИОНИН (полная выдача)
        (3, 3, '2024-01-22', 0.5),  # Абакумов - АДЕМЕТИОНИН (частичная выдача)
    ]
    
    for dispensing in dispensings_data:
        db.execute('''
            INSERT INTO dispensings (patient_id, medicine_id, dispensing_date, quantity_packs)
            VALUES (?, ?, ?, ?)
        ''', dispensing)
    
    db.commit()

def execute_query(query, params=None):
    """Выполнение SQL-запроса."""
    db = get_db()
    if params:
        cursor = db.execute(query, params)
    else:
        cursor = db.execute(query)
    return cursor

def execute_update(query, params=None):
    """Выполнение SQL-запроса на изменение данных."""
    db = get_db()
    if params:
        cursor = db.execute(query, params)
    else:
        cursor = db.execute(query)
    db.commit()
    return cursor.rowcount

def fetch_one(query, params=None):
    """Получение одной записи из базы данных."""
    cursor = execute_query(query, params)
    return cursor.fetchone()

def fetch_all(query, params=None):
    """Получение всех записей из базы данных."""
    cursor = execute_query(query, params)
    return cursor.fetchall()

def fetch_paginated(query, params=None, page=1, per_page=10):
    """
    Получение записей с поддержкой пагинации для работы с большими объемами данных.
    
    Args:
        query: SQL-запрос
        params: Параметры для запроса
        page: Номер страницы (начиная с 1)
        per_page: Количество записей на странице
    
    Returns:
        dict: Словарь с данными пагинации
    """
    # Подсчет общего количества записей
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total = fetch_one(count_query, params)[0]
    
    # Вычисление смещения
    offset = (page - 1) * per_page
    
    # Добавление LIMIT и OFFSET к основному запросу
    paginated_query = f"{query} LIMIT ? OFFSET ?"
    if params:
        paginated_params = list(params) + [per_page, offset]
    else:
        paginated_params = [per_page, offset]
    
    # Получение данных для текущей страницы
    items = fetch_all(paginated_query, paginated_params)
    
    # Вычисление информации о пагинации
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': page - 1 if has_prev else None,
        'next_num': page + 1 if has_next else None
    }

def search_with_pagination(table, search_fields, search_term, page=1, per_page=10, order_by=None):
    """
    Поиск записей с пагинацией для оптимизации работы с большими объемами данных.
    
    Args:
        table: Название таблицы
        search_fields: Список полей для поиска
        search_term: Поисковый запрос
        page: Номер страницы
        per_page: Количество записей на странице
        order_by: Поле для сортировки
    
    Returns:
        dict: Результаты поиска с пагинацией
    """
    if not search_term:
        query = f"SELECT * FROM {table}"
        if order_by:
            query += f" ORDER BY {order_by}"
        return fetch_paginated(query, None, page, per_page)
    
    # Создание условий поиска
    search_conditions = []
    params = []
    
    for field in search_fields:
        search_conditions.append(f"{field} LIKE ?")
        params.append(f"%{search_term}%")
    
    where_clause = " OR ".join(search_conditions)
    query = f"SELECT * FROM {table} WHERE {where_clause}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    return fetch_paginated(query, params, page, per_page)

def bulk_insert(table, columns, data_list, batch_size=1000):
    """
    Массовая вставка данных для оптимизации работы с большими объемами.
    
    Args:
        table: Название таблицы
        columns: Список названий колонок
        data_list: Список кортежей с данными
        batch_size: Размер пакета для вставки
    """
    db = get_db()
    
    placeholders = ', '.join(['?' for _ in columns])
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Обработка данных пакетами для оптимизации памяти
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i + batch_size]
        db.executemany(query, batch)
    
    db.commit()

def create_indexes_for_performance():
    """Создание дополнительных индексов для улучшения производительности."""
    db = get_db()
    
    # Композитные индексы для частых запросов
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_patients_fio_diagnosis ON patients (fio, diagnosis)',
        'CREATE INDEX IF NOT EXISTS idx_medicines_mnn_trade ON medicines (standardized_mnn, trade_name_vk)',
        'CREATE INDEX IF NOT EXISTS idx_prescriptions_date_patient ON prescriptions (prescription_date, patient_id)',
        'CREATE INDEX IF NOT EXISTS idx_dispensings_date_patient ON dispensings (dispensing_date, patient_id)',
        'CREATE INDEX IF NOT EXISTS idx_medicines_price ON medicines (price)',
        'CREATE INDEX IF NOT EXISTS idx_patients_birth_year ON patients (birth_year)',
    ]
    
    for index_query in indexes:
        db.execute(index_query)
    
    db.commit()

