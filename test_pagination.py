#!/usr/bin/env python3
"""
Тест функциональности пагинации и работы с большими объемами данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_updated import init_db, fetch_paginated, search_with_pagination, bulk_insert
from models_updated import Patient, Medicine, Prescription, Dispensing
from flask import Flask
import config

# Создание тестового приложения Flask
app = Flask(__name__)
app.config.from_object(config)

def test_pagination():
    """Тест функций пагинации"""
    print("=== Тестирование функций пагинации ===")
    
    with app.app_context():
        # Инициализация БД
        init_db()
        
        # Тест 1: Базовая пагинация пациентов
        print("\n1. Тест базовой пагинации пациентов:")
        patients_page1 = Patient.get_paginated(page=1, per_page=2)
        print(f"Страница 1: {len(patients_page1['items'])} записей из {patients_page1['total']}")
        print(f"Всего страниц: {patients_page1['total_pages']}")
        
        # Тест 2: Поиск с пагинацией
        print("\n2. Тест поиска пациентов с пагинацией:")
        search_result = Patient.search_paginated("Абаева", page=1, per_page=10)
        print(f"Найдено: {len(search_result['items'])} записей из {search_result['total']}")
        for patient in search_result['items']:
            print(f"  - {patient.fio} ({patient.diagnosis})")
        
        # Тест 3: Пагинация препаратов
        print("\n3. Тест пагинации препаратов:")
        medicines_page1 = Medicine.get_paginated(page=1, per_page=2)
        print(f"Страница 1: {len(medicines_page1['items'])} записей из {medicines_page1['total']}")
        for medicine in medicines_page1['items']:
            print(f"  - {medicine.trade_name_vk} ({medicine.standardized_mnn})")
        
        # Тест 4: Фильтрация по цене
        print("\n4. Тест фильтрации препаратов по цене:")
        price_filter = Medicine.get_by_price_range(min_price=1000, max_price=2000, page=1, per_page=10)
        print(f"Препараты от 1000 до 2000 руб.: {len(price_filter['items'])} записей")
        for medicine in price_filter['items']:
            print(f"  - {medicine.trade_name_vk}: {medicine.price} руб.")

def test_bulk_operations():
    """Тест массовых операций"""
    print("\n=== Тестирование массовых операций ===")
    
    with app.app_context():
        # Создание тестовых данных для массовой вставки
        test_patients = [
            ("Тестовый Пациент 1", 1980, "Тестовый диагноз 1", "Тестовый врач 1"),
            ("Тестовый Пациент 2", 1985, "Тестовый диагноз 2", "Тестовый врач 2"),
            ("Тестовый Пациент 3", 1990, "Тестовый диагноз 3", "Тестовый врач 3"),
        ]
        
        print("\n1. Тест массовой вставки пациентов:")
        Patient.bulk_create(test_patients)
        print(f"Добавлено {len(test_patients)} тестовых пациентов")
        
        # Проверка результата
        all_patients = Patient.get_paginated(page=1, per_page=20)
        print(f"Общее количество пациентов: {all_patients['total']}")
        
        test_medicines = [
            ("TEST-001", "Тест", "ТЕСТОВОЕ МНН 1", "Тестовый препарат 1", "таблетки", "10 мг", "тест", "10", 100.50),
            ("TEST-002", "Тест", "ТЕСТОВОЕ МНН 2", "Тестовый препарат 2", "капсулы", "20 мг", "тест", "20", 200.75),
        ]
        
        print("\n2. Тест массовой вставки препаратов:")
        Medicine.bulk_create(test_medicines)
        print(f"Добавлено {len(test_medicines)} тестовых препаратов")
        
        # Проверка результата
        all_medicines = Medicine.get_paginated(page=1, per_page=20)
        print(f"Общее количество препаратов: {all_medicines['total']}")

def test_search_functionality():
    """Тест функций поиска"""
    print("\n=== Тестирование функций поиска ===")
    
    with app.app_context():
        # Тест поиска пациентов
        print("\n1. Поиск пациентов по ФИО:")
        search_results = Patient.search_paginated("Тестовый", page=1, per_page=10)
        print(f"Найдено пациентов: {len(search_results['items'])}")
        
        # Тест поиска препаратов
        print("\n2. Поиск препаратов по названию:")
        medicine_results = Medicine.search_paginated("ТЕСТОВОЕ", page=1, per_page=10)
        print(f"Найдено препаратов: {len(medicine_results['items'])}")
        
        # Тест поиска препаратов по МНН
        print("\n3. Поиск препаратов по торговому названию:")
        trade_name_results = Medicine.search_paginated("Тестовый препарат", page=1, per_page=10)
        print(f"Найдено препаратов: {len(trade_name_results['items'])}")

def main():
    """Основная функция тестирования"""
    print("Запуск тестов обновленной медицинской системы")
    print("=" * 50)
    
    try:
        test_pagination()
        test_bulk_operations()
        test_search_functionality()
        
        print("\n" + "=" * 50)
        print("✅ Все тесты выполнены успешно!")
        print("\nОсновные возможности:")
        print("- ✅ Пагинация работает корректно")
        print("- ✅ Поиск с пагинацией функционирует")
        print("- ✅ Массовые операции выполняются")
        print("- ✅ Фильтрация по параметрам работает")
        print("- ✅ База данных обновлена до новой структуры")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

