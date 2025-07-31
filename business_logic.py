from database import fetch_all, fetch_one
from models import Patient, Medicine, Prescription, Dispensing
import csv
import io
from datetime import datetime

class BusinessLogic:
    """Класс для реализации бизнес-логики и расчётной логики системы."""
    
    @staticmethod
    def calculate_remaining_need(patient_id, medicine_id):
        """
        Расчёт остаточной потребности пациента в конкретном препарате.
        
        Args:
            patient_id (int): ID пациента
            medicine_id (int): ID препарата
            
        Returns:
            float: Остаточная потребность в упаковках
        """
        # Получение общего количества назначенных упаковок
        prescribed_query = """
            SELECT COALESCE(SUM(quantity_packs), 0) as total_prescribed
            FROM prescriptions 
            WHERE patient_id = ? AND medicine_id = ?
        """
        prescribed_result = fetch_one(prescribed_query, (patient_id, medicine_id))
        total_prescribed = prescribed_result['total_prescribed'] if prescribed_result else 0
        
        # Получение общего количества выданных упаковок
        dispensed_query = """
            SELECT COALESCE(SUM(quantity_packs), 0) as total_dispensed
            FROM dispensings 
            WHERE patient_id = ? AND medicine_id = ?
        """
        dispensed_result = fetch_one(dispensed_query, (patient_id, medicine_id))
        total_dispensed = dispensed_result['total_dispensed'] if dispensed_result else 0
        
        # Расчёт остаточной потребности
        remaining_need = total_prescribed - total_dispensed
        return max(0, remaining_need)  # Не может быть отрицательной
    
    @staticmethod
    def get_patient_medicine_summary(patient_id):
        """
        Получение сводной информации по всем препаратам для конкретного пациента.
        
        Args:
            patient_id (int): ID пациента
            
        Returns:
            list: Список словарей с информацией по каждому препарату
        """
        query = """
            SELECT DISTINCT 
                m.medicine_id,
                m.standardized_mnn,
                m.trade_name_vk,
                m.standardized_dosage_form,
                m.standardized_dosage,
                m.price
            FROM prescriptions p
            JOIN medicines m ON p.medicine_id = m.medicine_id
            WHERE p.patient_id = ?
            ORDER BY m.standardized_mnn
        """
        
        medicines = fetch_all(query, (patient_id,))
        summary = []
        
        for medicine in medicines:
            medicine_id = medicine['medicine_id']
            
            # Расчёт остаточной потребности
            remaining_need = BusinessLogic.calculate_remaining_need(patient_id, medicine_id)
            
            # Получение последнего назначения
            last_prescription_query = """
                SELECT prescription_date, quantity_packs
                FROM prescriptions
                WHERE patient_id = ? AND medicine_id = ?
                ORDER BY prescription_date DESC
                LIMIT 1
            """
            last_prescription = fetch_one(last_prescription_query, (patient_id, medicine_id))
            
            # Получение последней выдачи
            last_dispensing_query = """
                SELECT dispensing_date, quantity_packs
                FROM dispensings
                WHERE patient_id = ? AND medicine_id = ?
                ORDER BY dispensing_date DESC
                LIMIT 1
            """
            last_dispensing = fetch_one(last_dispensing_query, (patient_id, medicine_id))
            
            summary.append({
                'medicine_id': medicine_id,
                'medicine_name': medicine['standardized_mnn'],
                'trade_name': medicine['trade_name_vk'],
                'dosage_form': medicine['standardized_dosage_form'],
                'dosage': medicine['standardized_dosage'],
                'price': medicine['price'],
                'remaining_need': remaining_need,
                'remaining_cost': remaining_need * medicine['price'],
                'last_prescription_date': last_prescription['prescription_date'] if last_prescription else None,
                'last_prescription_quantity': last_prescription['quantity_packs'] if last_prescription else 0,
                'last_dispensing_date': last_dispensing['dispensing_date'] if last_dispensing else None,
                'last_dispensing_quantity': last_dispensing['quantity_packs'] if last_dispensing else 0
            })
        
        return summary
    
    @staticmethod
    def generate_medicine_report():
        """
        Генерация сводного отчёта по всем препаратам с расчётом потребности.
        
        Returns:
            dict: Словарь с данными отчёта и итоговой статистикой
        """
        # Получение всех препаратов
        medicines = Medicine.get_all()
        report_data = []
        total_patients = 0
        total_cost = 0.0
        
        for medicine in medicines:
            # Получение всех пациентов, которым назначен данный препарат
            patients_query = """
                SELECT DISTINCT patient_id
                FROM prescriptions
                WHERE medicine_id = ?
            """
            patients_with_medicine = fetch_all(patients_query, (medicine.medicine_id,))
            
            patients_count = 0
            total_need = 0.0
            
            for patient_row in patients_with_medicine:
                patient_id = patient_row['patient_id']
                remaining_need = BusinessLogic.calculate_remaining_need(patient_id, medicine.medicine_id)
                
                if remaining_need > 0:
                    patients_count += 1
                    total_need += remaining_need
            
            # Добавление в отчёт только если есть потребность
            if patients_count > 0:
                medicine_cost = total_need * medicine.price
                total_patients += patients_count
                total_cost += medicine_cost
                
                report_data.append({
                    'medicine_id': medicine.medicine_id,
                    'smmn_node_code': medicine.smmn_node_code,
                    'section': medicine.section,
                    'standardized_mnn': medicine.standardized_mnn,
                    'trade_name_vk': medicine.trade_name_vk,
                    'standardized_dosage_form': medicine.standardized_dosage_form,
                    'standardized_dosage': medicine.standardized_dosage,
                    'characteristic': medicine.characteristic or '',
                    'packaging': medicine.packaging,
                    'price': medicine.price,
                    'patients_count': patients_count,
                    'total_need': total_need,
                    'total_cost': medicine_cost
                })
        
        # Сортировка по убыванию стоимости
        report_data.sort(key=lambda x: x['total_cost'], reverse=True)
        
        return {
            'data': report_data,
            'summary': {
                'total_medicines': len(report_data),
                'total_patients': total_patients,
                'total_cost': total_cost,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    
    @staticmethod
    def export_medicine_report_to_csv():
        """
        Экспорт отчёта по препаратам в формат CSV.
        
        Returns:
            str: CSV-данные в виде строки
        """
        report = BusinessLogic.generate_medicine_report()
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Заголовки
        headers = [
            'ID препарата',
            'Код СМНН',
            'Раздел',
            'Стандартизированное МНН',
            'Торговое наименование ВК',
            'Стандартизированная лекарственная форма',
            'Стандартизированная лекарственная доза',
            'Характеристика',
            'Фасовка',
            'Цена',
            'Количество пациентов',
            'Общая потребность',
            'Общая стоимость'
        ]
        writer.writerow(headers)
        
        # Данные
        for item in report['data']:
            row = [
                item['medicine_id'],
                item['smmn_node_code'],
                item['section'],
                item['standardized_mnn'],
                item['trade_name_vk'],
                item['standardized_dosage_form'],
                item['standardized_dosage'],
                item['characteristic'],
                item['packaging'],
                f"{item['price']:.2f}",
                item['patients_count'],
                f"{item['total_need']:.1f}",
                f"{item['total_cost']:.2f}"
            ]
            writer.writerow(row)
        
        # Итоговая строка
        writer.writerow([])
        writer.writerow([
            'ИТОГО:',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            report['summary']['total_patients'],
            '',
            f"{report['summary']['total_cost']:.2f}"
        ])
        
        # Информация о генерации
        writer.writerow([])
        writer.writerow(['Отчёт сгенерирован:', report['summary']['generated_at']])
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
    
    @staticmethod
    def validate_prescription(patient_id, medicine_id, quantity_packs):
        """
        Валидация назначения препарата.
        
        Args:
            patient_id (int): ID пациента
            medicine_id (int): ID препарата
            quantity_packs (float): Количество упаковок
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Проверка существования пациента
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return False, "Пациент не найден"
        
        # Проверка существования препарата
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return False, "Препарат не найден"
        
        # Проверка количества
        if quantity_packs <= 0:
            return False, "Количество упаковок должно быть больше нуля"
        
        if quantity_packs > 1000:  # Разумное ограничение
            return False, "Количество упаковок не может превышать 1000"
        
        return True, ""
    
    @staticmethod
    def validate_dispensing(patient_id, medicine_id, quantity_packs):
        """
        Валидация выдачи препарата.
        
        Args:
            patient_id (int): ID пациента
            medicine_id (int): ID препарата
            quantity_packs (float): Количество упаковок
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Базовая валидация
        is_valid, error_message = BusinessLogic.validate_prescription(patient_id, medicine_id, quantity_packs)
        if not is_valid:
            return is_valid, error_message
        
        # Проверка наличия назначений
        remaining_need = BusinessLogic.calculate_remaining_need(patient_id, medicine_id)
        if remaining_need <= 0:
            return False, "У пациента нет назначений данного препарата или они уже полностью выданы"
        
        # Проверка превышения назначенного количества
        if quantity_packs > remaining_need:
            return False, f"Количество к выдаче ({quantity_packs}) превышает остаточную потребность ({remaining_need:.1f})"
        
        return True, ""
    
    @staticmethod
    def get_medicine_usage_statistics():
        """
        Получение статистики использования препаратов.
        
        Returns:
            dict: Статистика по препаратам
        """
        # Топ-10 наиболее назначаемых препаратов
        top_prescribed_query = """
            SELECT 
                m.standardized_mnn,
                m.trade_name_vk,
                COUNT(DISTINCT p.patient_id) as patients_count,
                SUM(p.quantity_packs) as total_prescribed
            FROM prescriptions p
            JOIN medicines m ON p.medicine_id = m.medicine_id
            GROUP BY m.medicine_id, m.standardized_mnn, m.trade_name_vk
            ORDER BY patients_count DESC, total_prescribed DESC
            LIMIT 10
        """
        top_prescribed = fetch_all(top_prescribed_query)
        
        # Топ-10 наиболее выдаваемых препаратов
        top_dispensed_query = """
            SELECT 
                m.standardized_mnn,
                m.trade_name_vk,
                COUNT(DISTINCT d.patient_id) as patients_count,
                SUM(d.quantity_packs) as total_dispensed
            FROM dispensings d
            JOIN medicines m ON d.medicine_id = m.medicine_id
            GROUP BY m.medicine_id, m.standardized_mnn, m.trade_name_vk
            ORDER BY patients_count DESC, total_dispensed DESC
            LIMIT 10
        """
        top_dispensed = fetch_all(top_dispensed_query)
        
        # Общая статистика
        general_stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM patients) as total_patients,
                (SELECT COUNT(*) FROM medicines) as total_medicines,
                (SELECT COUNT(*) FROM prescriptions) as total_prescriptions,
                (SELECT COUNT(*) FROM dispensings) as total_dispensings,
                (SELECT COALESCE(SUM(quantity_packs), 0) FROM prescriptions) as total_prescribed_packs,
                (SELECT COALESCE(SUM(quantity_packs), 0) FROM dispensings) as total_dispensed_packs
        """
        general_stats = fetch_one(general_stats_query)
        
        return {
            'top_prescribed': [dict(row) for row in top_prescribed],
            'top_dispensed': [dict(row) for row in top_dispensed],
            'general_stats': dict(general_stats) if general_stats else {}
        }
    
    @staticmethod
    def get_patient_treatment_history(patient_id):
        """
        Получение истории лечения пациента.
        
        Args:
            patient_id (int): ID пациента
            
        Returns:
            dict: История назначений и выдач
        """
        # История назначений
        prescriptions_query = """
            SELECT 
                p.prescription_date,
                p.quantity_packs,
                m.standardized_mnn,
                m.trade_name_vk,
                m.standardized_dosage_form,
                m.standardized_dosage
            FROM prescriptions p
            JOIN medicines m ON p.medicine_id = m.medicine_id
            WHERE p.patient_id = ?
            ORDER BY p.prescription_date DESC
        """
        prescriptions = fetch_all(prescriptions_query, (patient_id,))
        
        # История выдач
        dispensings_query = """
            SELECT 
                d.dispensing_date,
                d.quantity_packs,
                m.standardized_mnn,
                m.trade_name_vk,
                m.standardized_dosage_form,
                m.standardized_dosage
            FROM dispensings d
            JOIN medicines m ON d.medicine_id = m.medicine_id
            WHERE d.patient_id = ?
            ORDER BY d.dispensing_date DESC
        """
        dispensings = fetch_all(dispensings_query, (patient_id,))
        
        return {
            'prescriptions': [dict(row) for row in prescriptions],
            'dispensings': [dict(row) for row in dispensings]
        }

