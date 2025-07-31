from database import execute_update, fetch_one, fetch_all

class Patient:
    def __init__(self, patient_id=None, fio=None, birth_year=None, diagnosis=None, attending_doctor=None):
        self.patient_id = patient_id
        self.fio = fio
        self.birth_year = birth_year
        self.diagnosis = diagnosis
        self.attending_doctor = attending_doctor

    def save(self):
        if self.patient_id is None:
            query = "INSERT INTO patients (fio, birth_year, diagnosis, attending_doctor) VALUES (?, ?, ?, ?)"
            execute_update(query, (self.fio, self.birth_year, self.diagnosis, self.attending_doctor))
        else:
            query = "UPDATE patients SET fio = ?, birth_year = ?, diagnosis = ?, attending_doctor = ? WHERE patient_id = ?"
            execute_update(query, (self.fio, self.birth_year, self.diagnosis, self.attending_doctor, self.patient_id))

    def delete(self):
        query = "DELETE FROM patients WHERE patient_id = ?"
        execute_update(query, (self.patient_id,))

    @staticmethod
    def get_by_id(patient_id):
        query = "SELECT * FROM patients WHERE patient_id = ?"
        row = fetch_one(query, (patient_id,))
        if row:
            return Patient(patient_id=row["patient_id"], fio=row["fio"], birth_year=row["birth_year"], diagnosis=row["diagnosis"], attending_doctor=row["attending_doctor"])
        return None

    @staticmethod
    def get_all():
        query = "SELECT * FROM patients"
        rows = fetch_all(query)
        return [Patient(patient_id=row["patient_id"], fio=row["fio"], birth_year=row["birth_year"], diagnosis=row["diagnosis"], attending_doctor=row["attending_doctor"]) for row in rows]

class Medicine:
    def __init__(self, medicine_id=None, smmn_node_code=None, section=None, standardized_mnn=None, trade_name_vk=None, standardized_dosage_form=None, standardized_dosage=None, characteristic=None, packaging=None, price=None):
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
        if self.medicine_id is None:
            query = "INSERT INTO medicines (smmn_node_code, section, standardized_mnn, trade_name_vk, standardized_dosage_form, standardized_dosage, characteristic, packaging, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            execute_update(query, (self.smmn_node_code, self.section, self.standardized_mnn, self.trade_name_vk, self.standardized_dosage_form, self.standardized_dosage, self.characteristic, self.packaging, self.price))
        else:
            query = "UPDATE medicines SET smmn_node_code = ?, section = ?, standardized_mnn = ?, trade_name_vk = ?, standardized_dosage_form = ?, standardized_dosage = ?, characteristic = ?, packaging = ?, price = ? WHERE medicine_id = ?"
            execute_update(query, (self.smmn_node_code, self.section, self.standardized_mnn, self.trade_name_vk, self.standardized_dosage_form, self.standardized_dosage, self.characteristic, self.packaging, self.price, self.medicine_id))

    def delete(self):
        query = "DELETE FROM medicines WHERE medicine_id = ?"
        execute_update(query, (self.medicine_id,))

    @staticmethod
    def get_by_id(medicine_id):
        query = "SELECT * FROM medicines WHERE medicine_id = ?"
        row = fetch_one(query, (medicine_id,))
        if row:
            return Medicine(medicine_id=row["medicine_id"], smmn_node_code=row["smmn_node_code"], section=row["section"], standardized_mnn=row["standardized_mnn"], trade_name_vk=row["trade_name_vk"], standardized_dosage_form=row["standardized_dosage_form"], standardized_dosage=row["standardized_dosage"], characteristic=row["characteristic"], packaging=row["packaging"], price=row["price"])
        return None

    @staticmethod
    def get_all():
        query = "SELECT * FROM medicines"
        rows = fetch_all(query)
        return [Medicine(medicine_id=row["medicine_id"], smmn_node_code=row["smmn_node_code"], section=row["section"], standardized_mnn=row["standardized_mnn"], trade_name_vk=row["trade_name_vk"], standardized_dosage_form=row["standardized_dosage_form"], standardized_dosage=row["standardized_dosage"], characteristic=row["characteristic"], packaging=row["packaging"], price=row["price"]) for row in rows]

class Prescription:
    def __init__(self, prescription_id=None, patient_id=None, medicine_id=None, prescription_date=None, quantity_packs=None):
        self.prescription_id = prescription_id
        self.patient_id = patient_id
        self.medicine_id = medicine_id
        self.prescription_date = prescription_date
        self.quantity_packs = quantity_packs

    def save(self):
        if self.prescription_id is None:
            query = "INSERT INTO prescriptions (patient_id, medicine_id, prescription_date, quantity_packs) VALUES (?, ?, ?, ?)"
            execute_update(query, (self.patient_id, self.medicine_id, self.prescription_date, self.quantity_packs))
        else:
            query = "UPDATE prescriptions SET patient_id = ?, medicine_id = ?, prescription_date = ?, quantity_packs = ? WHERE prescription_id = ?"
            execute_update(query, (self.patient_id, self.medicine_id, self.prescription_date, self.quantity_packs, self.prescription_id))

    def delete(self):
        query = "DELETE FROM prescriptions WHERE prescription_id = ?"
        execute_update(query, (self.prescription_id,))

    @staticmethod
    def get_by_id(prescription_id):
        query = "SELECT * FROM prescriptions WHERE prescription_id = ?"
        row = fetch_one(query, (prescription_id,))
        if row:
            return Prescription(prescription_id=row["prescription_id"], patient_id=row["patient_id"], medicine_id=row["medicine_id"], prescription_date=row["prescription_date"], quantity_packs=row["quantity_packs"])
        return None

    @staticmethod
    def get_all():
        query = "SELECT * FROM prescriptions"
        rows = fetch_all(query)
        return [Prescription(prescription_id=row["prescription_id"], patient_id=row["patient_id"], medicine_id=row["medicine_id"], prescription_date=row["prescription_date"], quantity_packs=row["quantity_packs"]) for row in rows]

class Dispensing:
    def __init__(self, dispensing_id=None, patient_id=None, medicine_id=None, dispensing_date=None, quantity_packs=None):
        self.dispensing_id = dispensing_id
        self.patient_id = patient_id
        self.medicine_id = medicine_id
        self.dispensing_date = dispensing_date
        self.quantity_packs = quantity_packs

    def save(self):
        if self.dispensing_id is None:
            query = "INSERT INTO dispensings (patient_id, medicine_id, dispensing_date, quantity_packs) VALUES (?, ?, ?, ?)"
            execute_update(query, (self.patient_id, self.medicine_id, self.dispensing_date, self.quantity_packs))
        else:
            query = "UPDATE dispensings SET patient_id = ?, medicine_id = ?, dispensing_date = ?, quantity_packs = ? WHERE dispensing_id = ?"
            execute_update(query, (self.patient_id, self.medicine_id, self.dispensing_date, self.quantity_packs, self.dispensing_id))

    def delete(self):
        query = "DELETE FROM dispensings WHERE dispensing_id = ?"
        execute_update(query, (self.dispensing_id,))

    @staticmethod
    def get_by_id(dispensing_id):
        query = "SELECT * FROM dispensings WHERE dispensing_id = ?"
        row = fetch_one(query, (dispensing_id,))
        if row:
            return Dispensing(dispensing_id=row["dispensing_id"], patient_id=row["patient_id"], medicine_id=row["medicine_id"], dispensing_date=row["dispensing_date"], quantity_packs=row["quantity_packs"])
        return None

    @staticmethod
    def get_all():
        query = "SELECT * FROM dispensings"
        rows = fetch_all(query)
        return [Dispensing(dispensing_id=row["dispensing_id"], patient_id=row["patient_id"], medicine_id=row["medicine_id"], dispensing_date=row["dispensing_date"], quantity_packs=row["quantity_packs"]) for row in rows]


