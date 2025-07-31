"""
Модуль для генерации различных отчетов в медицинской информационной системе.
"""

from database import fetch_all, fetch_one
from datetime import datetime, timedelta
import csv
import io

class ReportsGenerator:
    """Класс для генерации отчетов."""
    
    @staticmethod
    def generate_patient_report(start_date=None, end_date=None, patient_id=None):
        """
        Генерирует отчет по пациентам.
        
        Args:
            start_date (str): Начальная дата в формате YYYY-MM-DD
            end_date (str): Конечная дата в формате YYYY-MM-DD
            patient_id (int): ID конкретного пациента (опционально)
            
        Returns:
            dict: Отчет по пациентам
        """
        # Базовый запрос
        base_query = """
            SELECT 
                p.patient_id,
                p.fio,
                p.birth_year,
                p.diagnosis,
                p.attending_doctor,
                COUNT(DISTINCT pr.prescription_id) as total_prescriptions,
                COUNT(DISTINCT d.dispensing_id) as total_dispensings,
                COALESCE(SUM(pr.quantity_packs), 0) as total_prescribed_packs,
                COALESCE(SUM(d.quantity_packs), 0) as total_dispensed_packs,
                COALESCE(SUM(d.quantity_packs * m.price), 0) as total_cost
            FROM patients p
            LEFT JOIN prescriptions pr ON p.patient_id = pr.patient_id
            LEFT JOIN dispensings d ON p.patient_id = d.patient_id
            LEFT JOIN medicines m ON d.medicine_id = m.medicine_id
        """
        
        conditions = []
        params = []
        
        # Добавляем условия фильтрации
        if patient_id:
            conditions.append("p.patient_id = ?")
            params.append(patient_id)
            
        if start_date:
            conditions.append("(pr.prescription_date >= ? OR d.dispensing_date >= ?)")
            params.extend([start_date, start_date])
            
        if end_date:
            conditions.append("(pr.prescription_date <= ? OR d.dispensing_date <= ?)")
            params.extend([end_date, end_date])
        
        # Формируем финальный запрос
        if conditions:
            query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            query = base_query
            
        query += " GROUP BY p.patient_id ORDER BY p.fio"
        
        # Выполняем запрос
        patients_data = fetch_all(query, params if params else None)
        
        # Подсчитываем общую статистику
        total_patients = len(patients_data)
        total_prescriptions = sum(row['total_prescriptions'] for row in patients_data)
        total_dispensings = sum(row['total_dispensings'] for row in patients_data)
        total_cost = sum(row['total_cost'] for row in patients_data)
        
        return {
            'patients': patients_data,
            'summary': {
                'total_patients': total_patients,
                'total_prescriptions': total_prescriptions,
                'total_dispensings': total_dispensings,
                'total_cost': total_cost,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            },
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def generate_dispensing_report(start_date=None, end_date=None, medicine_id=None):
        """
        Генерирует отчет по выдачам.
        
        Args:
            start_date (str): Начальная дата в формате YYYY-MM-DD
            end_date (str): Конечная дата в формате YYYY-MM-DD
            medicine_id (int): ID конкретного препарата (опционально)
            
        Returns:
            dict: Отчет по выдачам
        """
        # Базовый запрос
        base_query = """
            SELECT 
                d.dispensing_id,
                d.dispensing_date,
                p.fio as patient_name,
                p.diagnosis,
                m.trade_name_vk as medicine_name,
                m.standardized_mnn,
                m.standardized_dosage,
                m.standardized_dosage_form,
                d.quantity_packs,
                m.price,
                (d.quantity_packs * m.price) as total_cost,
                pr.daily_dose,
                pr.treatment_days
            FROM dispensings d
            JOIN patients p ON d.patient_id = p.patient_id
            JOIN medicines m ON d.medicine_id = m.medicine_id
            LEFT JOIN prescriptions pr ON d.patient_id = pr.patient_id AND d.medicine_id = pr.medicine_id
        """
        
        conditions = []
        params = []
        
        # Добавляем условия фильтрации
        if start_date:
            conditions.append("d.dispensing_date >= ?")
            params.append(start_date)
            
        if end_date:
            conditions.append("d.dispensing_date <= ?")
            params.append(end_date)
            
        if medicine_id:
            conditions.append("d.medicine_id = ?")
            params.append(medicine_id)
        
        # Формируем финальный запрос
        if conditions:
            query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            query = base_query
            
        query += " ORDER BY d.dispensing_date DESC, p.fio"
        
        # Выполняем запрос
        dispensings_data = fetch_all(query, params if params else None)
        
        # Подсчитываем статистику по препаратам
        medicine_stats_query = """
            SELECT 
                m.medicine_id,
                m.trade_name_vk,
                m.standardized_mnn,
                COUNT(d.dispensing_id) as dispensing_count,
                SUM(d.quantity_packs) as total_packs,
                SUM(d.quantity_packs * m.price) as total_revenue
            FROM dispensings d
            JOIN medicines m ON d.medicine_id = m.medicine_id
        """
        
        if conditions:
            medicine_stats_query += " WHERE " + " AND ".join(conditions)
            
        medicine_stats_query += " GROUP BY m.medicine_id ORDER BY total_revenue DESC"
        
        medicine_stats = fetch_all(medicine_stats_query, params if params else None)
        
        # Общая статистика
        total_dispensings = len(dispensings_data)
        total_packs = sum(row['quantity_packs'] for row in dispensings_data)
        total_revenue = sum(row['total_cost'] for row in dispensings_data)
        
        return {
            'dispensings': dispensings_data,
            'medicine_statistics': medicine_stats,
            'summary': {
                'total_dispensings': total_dispensings,
                'total_packs': total_packs,
                'total_revenue': total_revenue,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            },
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def generate_financial_report(start_date=None, end_date=None):
        """
        Генерирует финансовый отчет.
        
        Args:
            start_date (str): Начальная дата в формате YYYY-MM-DD
            end_date (str): Конечная дата в формате YYYY-MM-DD
            
        Returns:
            dict: Финансовый отчет
        """
        # Доходы по выдачам
        revenue_query = """
            SELECT 
                d.dispensing_date,
                SUM(d.quantity_packs * m.price) as daily_revenue,
                COUNT(d.dispensing_id) as dispensings_count
            FROM dispensings d
            JOIN medicines m ON d.medicine_id = m.medicine_id
        """
        
        conditions = []
        params = []
        
        if start_date:
            conditions.append("d.dispensing_date >= ?")
            params.append(start_date)
            
        if end_date:
            conditions.append("d.dispensing_date <= ?")
            params.append(end_date)
        
        if conditions:
            revenue_query += " WHERE " + " AND ".join(conditions)
            
        revenue_query += " GROUP BY d.dispensing_date ORDER BY d.dispensing_date"
        
        daily_revenue = fetch_all(revenue_query, params if params else None)
        
        # Топ препаратов по доходам
        top_medicines_query = """
            SELECT 
                m.trade_name_vk,
                m.standardized_mnn,
                m.price,
                SUM(d.quantity_packs) as total_packs_sold,
                SUM(d.quantity_packs * m.price) as total_revenue,
                COUNT(DISTINCT d.patient_id) as unique_patients
            FROM dispensings d
            JOIN medicines m ON d.medicine_id = m.medicine_id
        """
        
        if conditions:
            top_medicines_query += " WHERE " + " AND ".join(conditions)
            
        top_medicines_query += " GROUP BY m.medicine_id ORDER BY total_revenue DESC LIMIT 10"
        
        top_medicines = fetch_all(top_medicines_query, params if params else None)
        
        # Статистика по врачам
        doctors_stats_query = """
            SELECT 
                p.attending_doctor,
                COUNT(DISTINCT d.dispensing_id) as dispensings_count,
                COUNT(DISTINCT d.patient_id) as patients_count,
                SUM(d.quantity_packs * m.price) as total_revenue
            FROM dispensings d
            JOIN patients p ON d.patient_id = p.patient_id
            JOIN medicines m ON d.medicine_id = m.medicine_id
        """
        
        if conditions:
            doctors_stats_query += " WHERE " + " AND ".join(conditions)
            
        doctors_stats_query += " GROUP BY p.attending_doctor ORDER BY total_revenue DESC"
        
        doctors_stats = fetch_all(doctors_stats_query, params if params else None)
        
        # Общая статистика
        total_revenue = sum(row['daily_revenue'] for row in daily_revenue)
        total_dispensings = sum(row['dispensings_count'] for row in daily_revenue)
        
        # Средние показатели
        avg_daily_revenue = total_revenue / len(daily_revenue) if daily_revenue else 0
        avg_dispensing_value = total_revenue / total_dispensings if total_dispensings > 0 else 0
        
        return {
            'daily_revenue': daily_revenue,
            'top_medicines': top_medicines,
            'doctors_statistics': doctors_stats,
            'summary': {
                'total_revenue': total_revenue,
                'total_dispensings': total_dispensings,
                'avg_daily_revenue': avg_daily_revenue,
                'avg_dispensing_value': avg_dispensing_value,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            },
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def export_report_to_csv(report_data, report_type):
        """
        Экспортирует отчет в CSV формат.
        
        Args:
            report_data (dict): Данные отчета
            report_type (str): Тип отчета ('patient', 'dispensing', 'financial')
            
        Returns:
            str: CSV содержимое
        """
        output = io.StringIO()
        
        if report_type == 'patient':
            writer = csv.writer(output)
            writer.writerow(['ФИО', 'Год рождения', 'Диагноз', 'Лечащий врач', 
                           'Назначений', 'Выдач', 'Назначено упаковок', 'Выдано упаковок', 'Общая стоимость'])
            
            for patient in report_data['patients']:
                writer.writerow([
                    patient['fio'],
                    patient['birth_year'],
                    patient['diagnosis'],
                    patient['attending_doctor'],
                    patient['total_prescriptions'],
                    patient['total_dispensings'],
                    patient['total_prescribed_packs'],
                    patient['total_dispensed_packs'],
                    f"{patient['total_cost']:.2f}"
                ])
                
        elif report_type == 'dispensing':
            writer = csv.writer(output)
            writer.writerow(['Дата выдачи', 'Пациент', 'Диагноз', 'Препарат', 
                           'МНН', 'Дозировка', 'Форма выпуска', 'Количество упаковок', 
                           'Цена за упаковку', 'Общая стоимость'])
            
            for dispensing in report_data['dispensings']:
                writer.writerow([
                    dispensing['dispensing_date'],
                    dispensing['patient_name'],
                    dispensing['diagnosis'],
                    dispensing['medicine_name'],
                    dispensing['standardized_mnn'],
                    dispensing['standardized_dosage'],
                    dispensing['standardized_dosage_form'],
                    dispensing['quantity_packs'],
                    f"{dispensing['price']:.2f}",
                    f"{dispensing['total_cost']:.2f}"
                ])
                
        elif report_type == 'financial':
            writer = csv.writer(output)
            writer.writerow(['Препарат', 'МНН', 'Цена за упаковку', 
                           'Продано упаковок', 'Общий доход', 'Уникальных пациентов'])
            
            for medicine in report_data['top_medicines']:
                writer.writerow([
                    medicine['trade_name_vk'],
                    medicine['standardized_mnn'],
                    f"{medicine['price']:.2f}",
                    medicine['total_packs_sold'],
                    f"{medicine['total_revenue']:.2f}",
                    medicine['unique_patients']
                ])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    @staticmethod
    def get_date_range_presets():
        """
        Возвращает предустановленные диапазоны дат для отчетов.
        
        Returns:
            dict: Словарь с предустановленными диапазонами
        """
        today = datetime.now().date()
        
        return {
            'today': {
                'start': today.strftime('%Y-%m-%d'),
                'end': today.strftime('%Y-%m-%d'),
                'label': 'Сегодня'
            },
            'yesterday': {
                'start': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
                'end': (today - timedelta(days=1)).strftime('%Y-%m-%d'),
                'label': 'Вчера'
            },
            'last_7_days': {
                'start': (today - timedelta(days=7)).strftime('%Y-%m-%d'),
                'end': today.strftime('%Y-%m-%d'),
                'label': 'Последние 7 дней'
            },
            'last_30_days': {
                'start': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
                'end': today.strftime('%Y-%m-%d'),
                'label': 'Последние 30 дней'
            },
            'current_month': {
                'start': today.replace(day=1).strftime('%Y-%m-%d'),
                'end': today.strftime('%Y-%m-%d'),
                'label': 'Текущий месяц'
            },
            'last_month': {
                'start': (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime('%Y-%m-%d'),
                'end': (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m-%d'),
                'label': 'Прошлый месяц'
            }
        }

