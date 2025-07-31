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
    
    # Создание таблицы пациентов
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
    
    # Создание таблицы медицинских препаратов
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
            packaging INTEGER NOT NULL,
            price REAL NOT NULL,
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
    
    # Создание индексов для улучшения производительности
    db.execute('CREATE INDEX IF NOT EXISTS idx_prescriptions_patient_medicine ON prescriptions (patient_id, medicine_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_dispensings_patient_medicine ON dispensings (patient_id, medicine_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_prescriptions_date ON prescriptions (prescription_date)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_dispensings_date ON dispensings (dispensing_date)')
    
    db.commit()

def insert_sample_data():
    """Вставка примерных данных для демонстрации."""
    db = get_db()
    
    # Проверяем, есть ли уже данные
    cursor = db.execute('SELECT COUNT(*) FROM patients')
    if cursor.fetchone()[0] > 0:
        return  # Данные уже есть
    
    # Добавление примерных пациентов
    patients_data = [
        ('Иванов Иван Иванович', 1980, 'Гипертония', 'Петров П.П.'),
        ('Петрова Мария Сергеевна', 1975, 'Диабет 2 типа', 'Сидоров С.С.'),
        ('Сидоров Алексей Николаевич', 1990, 'Бронхиальная астма', 'Петров П.П.'),
    ]
    
    for patient in patients_data:
        db.execute('''
            INSERT INTO patients (fio, birth_year, diagnosis, attending_doctor)
            VALUES (?, ?, ?, ?)
        ''', patient)
    
    # Добавление примерных медицинских препаратов
    medicines_data = [
        ('C09AA01', 'Сердечно-сосудистые препараты', 'Эналаприл', 'Эналаприл-Акрихин', 'таблетки', '10 мг', 'покрытые пленочной оболочкой', 20, 150.50),
        ('A10BA02', 'Препараты для лечения диабета', 'Метформин', 'Сиофор', 'таблетки', '500 мг', 'покрытые пленочной оболочкой', 30, 280.00),
        ('R03AC02', 'Препараты для лечения астмы', 'Сальбутамол', 'Вентолин', 'аэрозоль', '100 мкг/доза', 'для ингаляций дозированный', 1, 320.75),
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
        (1, 1, '2024-01-15', 2.0),  # Иванов - Эналаприл
        (2, 2, '2024-01-16', 1.5),  # Петрова - Метформин
        (3, 3, '2024-01-17', 1.0),  # Сидоров - Сальбутамол
    ]
    
    for prescription in prescriptions_data:
        db.execute('''
            INSERT INTO prescriptions (patient_id, medicine_id, prescription_date, quantity_packs)
            VALUES (?, ?, ?, ?)
        ''', prescription)
    
    # Добавление примерных выдач
    dispensings_data = [
        (1, 1, '2024-01-20', 1.0),  # Иванов - Эналаприл (частичная выдача)
        (2, 2, '2024-01-21', 1.5),  # Петрова - Метформин (полная выдача)
        (3, 3, '2024-01-22', 0.5),  # Сидоров - Сальбутамол (частичная выдача)
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

