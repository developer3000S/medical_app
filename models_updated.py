from database_updated import execute_update, fetch_one, fetch_all, fetch_paginated, search_with_pagination, bulk_insert

class Patient:
    def __init__(self, patient_id=None, fio=None, birth_year=None, diagnosis=None, attending_doctor=None):
        self.patient_id = patient_id
        self.fio = fio
        self.birth_year = birth_year
        self.diagnosis = diagnosis
        self.attending_doctor = attending_doctor

    def save(self):
        """Сохранение пациента с обновлением updated_at."""
        if self.patient_id is None:
            query = """
                INSERT INTO patients (fio, birth_year, diagnosis, attending_doctor)
                VALUES (?, ?, ?, ?)
            """
            execute_update(query, (self.fio, self.birth_year, self.diagnosis, self.attending_doctor))
        else:
            query = """
                UPDATE patients 
                SET fio = ?, birth_year = ?, diagnosis = ?, attending_doctor = ?, updated_at = CURRENT_TIMESTAMP
                WHERE patient_id = ?
            """
            execute_update(query, (self.fio, self.birth_year, self.diagnosis, self.attending_doctor, self.patient_id))

    def delete(self):
        """Удаление пациента."""
        query = "DELETE FROM patients WHERE patient_id = ?"
        execute_update(query, (self.patient_id,))

    @staticmethod
    def get_by_id(patient_id):
        """Получение пациента по ID."""
        query = "SELECT * FROM patients WHERE patient_id = ?"
        row = fetch_one(query, (patient_id,))
        if row:
            return Patient(
                patient_id=row["patient_id"], 
                fio=row["fio"], 
                birth_year=row["birth_year"], 
                diagnosis=row["diagnosis"], 
                attending_doctor=row["attending_doctor"]
            )
        return None

    @staticmethod
    def get_all():
        """Получение всех пациентов (для обратной совместимости)."""
        query = "SELECT * FROM patients ORDER BY fio"
        rows = fetch_all(query)
        return [Patient(
            patient_id=row["patient_id"], 
            fio=row["fio"], 
            birth_year=row["birth_year"], 
            diagnosis=row["diagnosis"], 
            attending_doctor=row["attending_doctor"]
        ) for row in rows]

    @staticmethod
    def get_paginated(page=1, per_page=10, order_by="fio"):
        """
        Получение пациентов с пагинацией для работы с большими объемами данных.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество записей на странице
            order_by: Поле для сортировки
        
        Returns:
            dict: Данные с пагинацией
        """
        query = f"SELECT * FROM patients ORDER BY {order_by}"
        result = fetch_paginated(query, None, page, per_page)
        
        # Преобразование строк в объекты Patient
        result['items'] = [Patient(
            patient_id=row["patient_id"], 
            fio=row["fio"], 
            birth_year=row["birth_year"], 
            diagnosis=row["diagnosis"], 
            attending_doctor=row["attending_doctor"]
        ) for row in result['items']]
        
        return result

    @staticmethod
    def search_paginated(search_term, page=1, per_page=10):
        """
        Поиск пациентов с пагинацией.
        
        Args:
            search_term: Поисковый запрос
            page: Номер страницы
            per_page: Количество записей на странице
        
        Returns:
            dict: Результаты поиска с пагинацией
        """
        search_fields = ['fio', 'diagnosis', 'attending_doctor']
        result = search_with_pagination('patients', search_fields, search_term, page, per_page, 'fio')
        
        # Преобразование строк в объекты Patient
        result['items'] = [Patient(
            patient_id=row["patient_id"], 
            fio=row["fio"], 
            birth_year=row["birth_year"], 
            diagnosis=row["diagnosis"], 
            attending_doctor=row["attending_doctor"]
        ) for row in result['items']]
        
        return result

    @staticmethod
    def bulk_create(patients_data):
        """
        Массовое создание пациентов для импорта больших объемов данных.
        
        Args:
            patients_data: Список кортежей (fio, birth_year, diagnosis, attending_doctor)
        """
        columns = ['fio', 'birth_year', 'diagnosis', 'attending_doctor']
        bulk_insert('patients', columns, patients_data)

class Medicine:
    def __init__(self, medicine_id=None, smmn_node_code=None, section=None, standardized_mnn=None, 
                 trade_name_vk=None, standardized_dosage_form=None, standardized_dosage=None, 
                 characteristic=None, packaging=None, price=None):
        self.medicine_id = medicine_id
        self.smmn_node_code = smmn_node_code
        self.section = section
        self.standardized_mnn = standardized_mnn
        self.trade_name_vk = trade_name_vk
        self.standardized_dosage_form = standardized_dosage_form
        self.standardized_dosage = standardized_dosage
        self.characteristic = characteristic
        self.packaging = packaging
        self.price = price

    def save(self):
        """Сохранение препарата с обновлением updated_at."""
        if self.medicine_id is None:
            query = """
                INSERT INTO medicines (smmn_node_code, section, standardized_mnn, trade_name_vk, 
                                     standardized_dosage_form, standardized_dosage, characteristic, 
                                     packaging, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            execute_update(query, (
                self.smmn_node_code, self.section, self.standardized_mnn, self.trade_name_vk,
                self.standardized_dosage_form, self.standardized_dosage, self.characteristic,
                self.packaging, self.price
            ))
        else:
            query = """
                UPDATE medicines 
                SET smmn_node_code = ?, section = ?, standardized_mnn = ?, trade_name_vk = ?, 
                    standardized_dosage_form = ?, standardized_dosage = ?, characteristic = ?, 
                    packaging = ?, price = ?, updated_at = CURRENT_TIMESTAMP
                WHERE medicine_id = ?
            """
            execute_update(query, (
                self.smmn_node_code, self.section, self.standardized_mnn, self.trade_name_vk,
                self.standardized_dosage_form, self.standardized_dosage, self.characteristic,
                self.packaging, self.price, self.medicine_id
            ))

    def delete(self):
        """Удаление препарата."""
        query = "DELETE FROM medicines WHERE medicine_id = ?"
        execute_update(query, (self.medicine_id,))

    @staticmethod
    def get_by_id(medicine_id):
        """Получение препарата по ID."""
        query = "SELECT * FROM medicines WHERE medicine_id = ?"
        row = fetch_one(query, (medicine_id,))
        if row:
            return Medicine(
                medicine_id=row["medicine_id"], 
                smmn_node_code=row["smmn_node_code"], 
                section=row["section"], 
                standardized_mnn=row["standardized_mnn"], 
                trade_name_vk=row["trade_name_vk"], 
                standardized_dosage_form=row["standardized_dosage_form"], 
                standardized_dosage=row["standardized_dosage"], 
                characteristic=row["characteristic"], 
                packaging=row["packaging"], 
                price=row["price"]
            )
        return None

    @staticmethod
    def get_all():
        """Получение всех препаратов (для обратной совместимости)."""
        query = "SELECT * FROM medicines ORDER BY trade_name_vk"
        rows = fetch_all(query)
        return [Medicine(
            medicine_id=row["medicine_id"], 
            smmn_node_code=row["smmn_node_code"], 
            section=row["section"], 
            standardized_mnn=row["standardized_mnn"], 
            trade_name_vk=row["trade_name_vk"], 
            standardized_dosage_form=row["standardized_dosage_form"], 
            standardized_dosage=row["standardized_dosage"], 
            characteristic=row["characteristic"], 
            packaging=row["packaging"], 
            price=row["price"]
        ) for row in rows]

    @staticmethod
    def get_paginated(page=1, per_page=10, order_by="trade_name_vk"):
        """
        Получение препаратов с пагинацией для работы с большими объемами данных.
        
        Args:
            page: Номер страницы (начиная с 1)
            per_page: Количество записей на странице
            order_by: Поле для сортировки
        
        Returns:
            dict: Данные с пагинацией
        """
        query = f"SELECT * FROM medicines ORDER BY {order_by}"
        result = fetch_paginated(query, None, page, per_page)
        
        # Преобразование строк в объекты Medicine
        result['items'] = [Medicine(
            medicine_id=row["medicine_id"], 
            smmn_node_code=row["smmn_node_code"], 
            section=row["section"], 
            standardized_mnn=row["standardized_mnn"], 
            trade_name_vk=row["trade_name_vk"], 
            standardized_dosage_form=row["standardized_dosage_form"], 
            standardized_dosage=row["standardized_dosage"], 
            characteristic=row["characteristic"], 
            packaging=row["packaging"], 
            price=row["price"]
        ) for row in result['items']]
        
        return result

    @staticmethod
    def search_paginated(search_term, page=1, per_page=10):
        """
        Поиск препаратов с пагинацией.
        
        Args:
            search_term: Поисковый запрос
            page: Номер страницы
            per_page: Количество записей на странице
        
        Returns:
            dict: Результаты поиска с пагинацией
        """
        search_fields = ['trade_name_vk', 'standardized_mnn', 'section']
        result = search_with_pagination('medicines', search_fields, search_term, page, per_page, 'trade_name_vk')
        
        # Преобразование строк в объекты Medicine
        result['items'] = [Medicine(
            medicine_id=row["medicine_id"], 
            smmn_node_code=row["smmn_node_code"], 
            section=row["section"], 
            standardized_mnn=row["standardized_mnn"], 
            trade_name_vk=row["trade_name_vk"], 
            standardized_dosage_form=row["standardized_dosage_form"], 
            standardized_dosage=row["standardized_dosage"], 
            characteristic=row["characteristic"], 
            packaging=row["packaging"], 
            price=row["price"]
        ) for row in result['items']]
        
        return result

    @staticmethod
    def bulk_create(medicines_data):
        """
        Массовое создание препаратов для импорта больших объемов данных.
        
        Args:
            medicines_data: Список кортежей с данными препаратов
        """
        columns = [
            'smmn_node_code', 'section', 'standardized_mnn', 'trade_name_vk',
            'standardized_dosage_form', 'standardized_dosage', 'characteristic',
            'packaging', 'price'
        ]
        bulk_insert('medicines', columns, medicines_data)

    @staticmethod
    def get_by_price_range(min_price=None, max_price=None, page=1, per_page=10):
        """
        Получение препаратов в определенном ценовом диапазоне с пагинацией.
        
        Args:
            min_price: Минимальная цена
            max_price: Максимальная цена
            page: Номер страницы
            per_page: Количество записей на странице
        
        Returns:
            dict: Результаты с пагинацией
        """
        conditions = []
        params = []
        
        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"SELECT * FROM medicines WHERE {where_clause} ORDER BY price"
        
        result = fetch_paginated(query, params, page, per_page)
        
        # Преобразование строк в объекты Medicine
        result['items'] = [Medicine(
            medicine_id=row["medicine_id"], 
            smmn_node_code=row["smmn_node_code"], 
            section=row["section"], 
            standardized_mnn=row["standardized_mnn"], 
            trade_name_vk=row["trade_name_vk"], 
            standardized_dosage_form=row["standardized_dosage_form"], 
            standardized_dosage=row["standardized_dosage"], 
            characteristic=row["characteristic"], 
            packaging=row["packaging"], 
            price=row["price"]
        ) for row in result['items']]
        
        return result

class Prescription:
    def __init__(self, prescription_id=None, patient_id=None, medicine_id=None, prescription_date=None, 
                 quantity_packs=None, daily_dose=None, treatment_days=None):
        self.prescription_id = prescription_id
        self.patient_id = patient_id
        self.medicine_id = medicine_id
        self.prescription_date = prescription_date
        self.quantity_packs = quantity_packs
        self.daily_dose = daily_dose
        self.treatment_days = treatment_days

    def save(self):
        """Сохранение назначения с обновлением updated_at."""
        if self.prescription_id is None:
            query = """
                INSERT INTO prescriptions (patient_id, medicine_id, prescription_date, quantity_packs, daily_dose, treatment_days)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            execute_update(query, (
                self.patient_id, self.medicine_id, self.prescription_date, 
                self.quantity_packs, self.daily_dose, self.treatment_days
            ))
        else:
            query = """
                UPDATE prescriptions 
                SET patient_id = ?, medicine_id = ?, prescription_date = ?, quantity_packs = ?, 
                    daily_dose = ?, treatment_days = ?, updated_at = CURRENT_TIMESTAMP
                WHERE prescription_id = ?
            """
            execute_update(query, (
                self.patient_id, self.medicine_id, self.prescription_date, 
                self.quantity_packs, self.daily_dose, self.treatment_days, self.prescription_id
            ))

    def delete(self):
        """Удаление назначения."""
        query = "DELETE FROM prescriptions WHERE prescription_id = ?"
        execute_update(query, (self.prescription_id,))

    @staticmethod
    def get_by_id(prescription_id):
        """Получение назначения по ID."""
        query = "SELECT * FROM prescriptions WHERE prescription_id = ?"
        row = fetch_one(query, (prescription_id,))
        if row:
            return Prescription(
                prescription_id=row["prescription_id"], 
                patient_id=row["patient_id"], 
                medicine_id=row["medicine_id"], 
                prescription_date=row["prescription_date"], 
                quantity_packs=row["quantity_packs"], 
                daily_dose=row.get("daily_dose"), 
                treatment_days=row.get("treatment_days")
            )
        return None

    @staticmethod
    def get_all():
        """Получение всех назначений (для обратной совместимости)."""
        query = "SELECT * FROM prescriptions ORDER BY prescription_date DESC"
        rows = fetch_all(query)
        return [Prescription(
            prescription_id=row["prescription_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            prescription_date=row["prescription_date"], 
            quantity_packs=row["quantity_packs"], 
            daily_dose=row.get("daily_dose"), 
            treatment_days=row.get("treatment_days")
        ) for row in rows]

    @staticmethod
    def get_paginated(page=1, per_page=10, order_by="prescription_date DESC"):
        """
        Получение назначений с пагинацией.
        
        Args:
            page: Номер страницы
            per_page: Количество записей на странице
            order_by: Поле для сортировки
        
        Returns:
            dict: Данные с пагинацией
        """
        query = f"SELECT * FROM prescriptions ORDER BY {order_by}"
        result = fetch_paginated(query, None, page, per_page)
        
        # Преобразование строк в объекты Prescription
        result['items'] = [Prescription(
            prescription_id=row["prescription_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            prescription_date=row["prescription_date"], 
            quantity_packs=row["quantity_packs"], 
            daily_dose=row.get("daily_dose"), 
            treatment_days=row.get("treatment_days")
        ) for row in result['items']]
        
        return result

    @staticmethod
    def get_by_patient_paginated(patient_id, page=1, per_page=10):
        """
        Получение назначений для конкретного пациента с пагинацией.
        
        Args:
            patient_id: ID пациента
            page: Номер страницы
            per_page: Количество записей на странице
        
        Returns:
            dict: Данные с пагинацией
        """
        query = "SELECT * FROM prescriptions WHERE patient_id = ? ORDER BY prescription_date DESC"
        result = fetch_paginated(query, (patient_id,), page, per_page)
        
        # Преобразование строк в объекты Prescription
        result['items'] = [Prescription(
            prescription_id=row["prescription_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            prescription_date=row["prescription_date"], 
            quantity_packs=row["quantity_packs"], 
            daily_dose=row.get("daily_dose"), 
            treatment_days=row.get("treatment_days")
        ) for row in result['items']]
        
        return result

class Dispensing:
    def __init__(self, dispensing_id=None, patient_id=None, medicine_id=None, dispensing_date=None, quantity_packs=None):
        self.dispensing_id = dispensing_id
        self.patient_id = patient_id
        self.medicine_id = medicine_id
        self.dispensing_date = dispensing_date
        self.quantity_packs = quantity_packs

    def save(self):
        """Сохранение выдачи с обновлением updated_at."""
        if self.dispensing_id is None:
            query = """
                INSERT INTO dispensings (patient_id, medicine_id, dispensing_date, quantity_packs)
                VALUES (?, ?, ?, ?)
            """
            execute_update(query, (self.patient_id, self.medicine_id, self.dispensing_date, self.quantity_packs))
        else:
            query = """
                UPDATE dispensings 
                SET patient_id = ?, medicine_id = ?, dispensing_date = ?, quantity_packs = ?, updated_at = CURRENT_TIMESTAMP
                WHERE dispensing_id = ?
            """
            execute_update(query, (
                self.patient_id, self.medicine_id, self.dispensing_date, 
                self.quantity_packs, self.dispensing_id
            ))

    def delete(self):
        """Удаление выдачи."""
        query = "DELETE FROM dispensings WHERE dispensing_id = ?"
        execute_update(query, (self.dispensing_id,))

    @staticmethod
    def get_by_id(dispensing_id):
        """Получение выдачи по ID."""
        query = "SELECT * FROM dispensings WHERE dispensing_id = ?"
        row = fetch_one(query, (dispensing_id,))
        if row:
            return Dispensing(
                dispensing_id=row["dispensing_id"], 
                patient_id=row["patient_id"], 
                medicine_id=row["medicine_id"], 
                dispensing_date=row["dispensing_date"], 
                quantity_packs=row["quantity_packs"]
            )
        return None

    @staticmethod
    def get_all():
        """Получение всех выдач (для обратной совместимости)."""
        query = "SELECT * FROM dispensings ORDER BY dispensing_date DESC"
        rows = fetch_all(query)
        return [Dispensing(
            dispensing_id=row["dispensing_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            dispensing_date=row["dispensing_date"], 
            quantity_packs=row["quantity_packs"]
        ) for row in rows]

    @staticmethod
    def get_paginated(page=1, per_page=10, order_by="dispensing_date DESC"):
        """
        Получение выдач с пагинацией.
        
        Args:
            page: Номер страницы
            per_page: Количество записей на странице
            order_by: Поле для сортировки
        
        Returns:
            dict: Данные с пагинацией
        """
        query = f"SELECT * FROM dispensings ORDER BY {order_by}"
        result = fetch_paginated(query, None, page, per_page)
        
        # Преобразование строк в объекты Dispensing
        result['items'] = [Dispensing(
            dispensing_id=row["dispensing_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            dispensing_date=row["dispensing_date"], 
            quantity_packs=row["quantity_packs"]
        ) for row in result['items']]
        
        return result

    @staticmethod
    def get_by_patient_paginated(patient_id, page=1, per_page=10):
        """
        Получение выдач для конкретного пациента с пагинацией.
        
        Args:
            patient_id: ID пациента
            page: Номер страницы
            per_page: Количество записей на странице
        
        Returns:
            dict: Данные с пагинацией
        """
        query = "SELECT * FROM dispensings WHERE patient_id = ? ORDER BY dispensing_date DESC"
        result = fetch_paginated(query, (patient_id,), page, per_page)
        
        # Преобразование строк в объекты Dispensing
        result['items'] = [Dispensing(
            dispensing_id=row["dispensing_id"], 
            patient_id=row["patient_id"], 
            medicine_id=row["medicine_id"], 
            dispensing_date=row["dispensing_date"], 
            quantity_packs=row["quantity_packs"]
        ) for row in result['items']]
        
        return result

