"""
Модуль для расчета дозировки и количества упаковок препаратов.
"""

import re
from models import Medicine

class DosageCalculator:
    """Класс для расчета дозировки и количества упаковок."""
    
    @staticmethod
    def extract_dosage_value(dosage_str):
        """
        Извлекает числовое значение дозировки из строки.
        
        Args:
            dosage_str (str): Строка с дозировкой (например, "10 мг", "500 мг", "100 мкг/доза")
            
        Returns:
            float: Числовое значение дозировки в мг
        """
        if not dosage_str:
            return 0.0
            
        # Ищем числовое значение в строке
        match = re.search(r'(\d+(?:\.\d+)?)', dosage_str)
        if not match:
            return 0.0
            
        value = float(match.group(1))
        
        # Проверяем единицы измерения
        if 'мкг' in dosage_str.lower() or 'mcg' in dosage_str.lower():
            # Конвертируем микрограммы в миллиграммы
            value = value / 1000
        elif 'г' in dosage_str.lower() and 'мг' not in dosage_str.lower():
            # Конвертируем граммы в миллиграммы
            value = value * 1000
            
        return value
    
    @staticmethod
    def calculate_required_packages(medicine_id, daily_dose_mg, treatment_days):
        """
        Рассчитывает необходимое количество упаковок препарата.
        
        Args:
            medicine_id (int): ID препарата
            daily_dose_mg (float): Суточная доза в мг
            treatment_days (int): Количество дней лечения
            
        Returns:
            dict: Словарь с результатами расчета
        """
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return {
                'success': False,
                'error': 'Препарат не найден',
                'packages_needed': 0,
                'total_dose_needed': 0,
                'dose_per_package': 0
            }
        
        # Извлекаем дозировку одной единицы препарата
        dose_per_unit = DosageCalculator.extract_dosage_value(medicine.standardized_dosage)
        
        if dose_per_unit <= 0:
            return {
                'success': False,
                'error': 'Не удалось определить дозировку препарата',
                'packages_needed': 0,
                'total_dose_needed': 0,
                'dose_per_package': 0
            }
        
        # Общая необходимая доза
        total_dose_needed = daily_dose_mg * treatment_days
        
        # Доза в одной упаковке
        dose_per_package = dose_per_unit * medicine.packaging
        
        # Необходимое количество упаковок (округляем вверх)
        packages_needed = total_dose_needed / dose_per_package
        packages_needed_rounded = int(packages_needed) + (1 if packages_needed % 1 > 0 else 0)
        
        return {
            'success': True,
            'error': None,
            'packages_needed': packages_needed_rounded,
            'packages_needed_exact': packages_needed,
            'total_dose_needed': total_dose_needed,
            'dose_per_package': dose_per_package,
            'dose_per_unit': dose_per_unit,
            'units_per_package': medicine.packaging,
            'medicine_name': medicine.trade_name_vk,
            'dosage_form': medicine.standardized_dosage_form
        }
    
    @staticmethod
    def validate_dosage_input(daily_dose, treatment_days):
        """
        Валидирует введенные данные о дозировке.
        
        Args:
            daily_dose (float): Суточная доза
            treatment_days (int): Количество дней лечения
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if daily_dose is None or daily_dose <= 0:
            return False, "Суточная доза должна быть больше 0"
            
        if treatment_days is None or treatment_days <= 0:
            return False, "Количество дней лечения должно быть больше 0"
            
        if treatment_days > 365:
            return False, "Количество дней лечения не может превышать 365 дней"
            
        if daily_dose > 10000:  # 10 грамм в мг
            return False, "Суточная доза слишком велика (максимум 10000 мг)"
            
        return True, None
    
    @staticmethod
    def get_dosage_recommendations(medicine_id):
        """
        Получает рекомендации по дозировке для препарата.
        
        Args:
            medicine_id (int): ID препарата
            
        Returns:
            dict: Рекомендации по дозировке
        """
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return None
            
        dose_per_unit = DosageCalculator.extract_dosage_value(medicine.standardized_dosage)
        
        # Базовые рекомендации в зависимости от формы выпуска
        recommendations = {
            'dose_per_unit': dose_per_unit,
            'units_per_package': medicine.packaging,
            'suggested_daily_doses': []
        }
        
        # Предлагаем типичные дозировки
        if 'таблетки' in medicine.standardized_dosage_form.lower():
            recommendations['suggested_daily_doses'] = [
                {'dose': dose_per_unit, 'description': '1 таблетка в день'},
                {'dose': dose_per_unit * 2, 'description': '2 таблетки в день'},
                {'dose': dose_per_unit * 3, 'description': '3 таблетки в день'}
            ]
        elif 'аэрозоль' in medicine.standardized_dosage_form.lower():
            recommendations['suggested_daily_doses'] = [
                {'dose': dose_per_unit * 2, 'description': '2 ингаляции в день'},
                {'dose': dose_per_unit * 4, 'description': '4 ингаляции в день'},
                {'dose': dose_per_unit * 6, 'description': '6 ингаляций в день'}
            ]
        else:
            recommendations['suggested_daily_doses'] = [
                {'dose': dose_per_unit, 'description': f'1 {medicine.standardized_dosage_form} в день'},
                {'dose': dose_per_unit * 2, 'description': f'2 {medicine.standardized_dosage_form} в день'}
            ]
            
        return recommendations

