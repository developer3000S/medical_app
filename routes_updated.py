from flask import render_template, request, redirect, url_for, flash, make_response, jsonify
from models_updated import Patient, Medicine, Prescription, Dispensing
from business_logic import BusinessLogic
from datetime import datetime

def init_routes(app):
    """Инициализация маршрутов Flask приложения с поддержкой пагинации."""
    
    @app.route("/")
    def index():
        """Главная страница."""
        return render_template("index.html")
    
    # Маршруты для пациентов с пагинацией
    @app.route("/patients")
    def patients():
        """Страница списка пациентов с пагинацией."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if search:
            pagination_data = Patient.search_paginated(search, page, per_page)
        else:
            pagination_data = Patient.get_paginated(page, per_page)
        
        return render_template("patients_paginated.html", 
                             patients=pagination_data['items'],
                             pagination=pagination_data,
                             search=search)
    
    @app.route("/patients/add", methods=["GET", "POST"])
    def add_patient():
        """Добавление нового пациента."""
        if request.method == "POST":
            try:
                patient = Patient(
                    fio=request.form["fio"].strip(),
                    birth_year=int(request.form["birth_year"]),
                    diagnosis=request.form["diagnosis"].strip(),
                    attending_doctor=request.form["attending_doctor"].strip()
                )
                patient.save()
                flash("Пациент успешно добавлен", "success")
                return redirect(url_for("patients"))
            except Exception as e:
                flash(f"Ошибка при добавлении пациента: {str(e)}", "error")
        
        return render_template("patient_form.html")
    
    @app.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
    def edit_patient(patient_id):
        """Редактирование пациента."""
        patient = Patient.get_by_id(patient_id)
        if not patient:
            flash("Пациент не найден", "error")
            return redirect(url_for("patients"))
        
        if request.method == "POST":
            try:
                patient.fio = request.form["fio"].strip()
                patient.birth_year = int(request.form["birth_year"])
                patient.diagnosis = request.form["diagnosis"].strip()
                patient.attending_doctor = request.form["attending_doctor"].strip()
                patient.save()
                flash("Данные пациента успешно обновлены", "success")
                return redirect(url_for("patients"))
            except Exception as e:
                flash(f"Ошибка при обновлении данных пациента: {str(e)}", "error")
        
        return render_template("patient_form.html", patient=patient)
    
    @app.route("/patients/delete/<int:patient_id>", methods=["POST"])
    def delete_patient(patient_id):
        """Удаление пациента."""
        patient = Patient.get_by_id(patient_id)
        if patient:
            try:
                patient.delete()
                flash("Пациент успешно удалён", "success")
            except Exception as e:
                flash(f"Ошибка при удалении пациента: {str(e)}", "error")
        else:
            flash("Пациент не найден", "error")
        
        return redirect(url_for("patients"))
    
    # Маршруты для препаратов с пагинацией
    @app.route("/medicines")
    def medicines():
        """Страница списка препаратов с пагинацией."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '', type=str)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if min_price is not None or max_price is not None:
            pagination_data = Medicine.get_by_price_range(min_price, max_price, page, per_page)
        elif search:
            pagination_data = Medicine.search_paginated(search, page, per_page)
        else:
            pagination_data = Medicine.get_paginated(page, per_page)
        
        return render_template("medicines_paginated.html", 
                             medicines=pagination_data['items'],
                             pagination=pagination_data,
                             search=search,
                             min_price=min_price,
                             max_price=max_price)
    
    @app.route("/medicines/add", methods=["GET", "POST"])
    def add_medicine():
        """Добавление нового препарата."""
        if request.method == "POST":
            try:
                medicine = Medicine(
                    smmn_node_code=request.form["smmn_node_code"].strip(),
                    section=request.form["section"].strip(),
                    standardized_mnn=request.form["standardized_mnn"].strip(),
                    trade_name_vk=request.form["trade_name_vk"].strip(),
                    standardized_dosage_form=request.form["standardized_dosage_form"].strip(),
                    standardized_dosage=request.form["standardized_dosage"].strip(),
                    characteristic=request.form.get("characteristic", "").strip(),
                    packaging=request.form["packaging"].strip(),
                    price=float(request.form["price"]) if request.form["price"] else None
                )
                medicine.save()
                flash("Препарат успешно добавлен", "success")
                return redirect(url_for("medicines"))
            except Exception as e:
                flash(f"Ошибка при добавлении препарата: {str(e)}", "error")
        
        return render_template("medicine_form.html")
    
    @app.route("/medicines/edit/<int:medicine_id>", methods=["GET", "POST"])
    def edit_medicine(medicine_id):
        """Редактирование препарата."""
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            flash("Препарат не найден", "error")
            return redirect(url_for("medicines"))
        
        if request.method == "POST":
            try:
                medicine.smmn_node_code = request.form["smmn_node_code"].strip()
                medicine.section = request.form["section"].strip()
                medicine.standardized_mnn = request.form["standardized_mnn"].strip()
                medicine.trade_name_vk = request.form["trade_name_vk"].strip()
                medicine.standardized_dosage_form = request.form["standardized_dosage_form"].strip()
                medicine.standardized_dosage = request.form["standardized_dosage"].strip()
                medicine.characteristic = request.form.get("characteristic", "").strip()
                medicine.packaging = request.form["packaging"].strip()
                medicine.price = float(request.form["price"]) if request.form["price"] else None
                medicine.save()
                flash("Данные препарата успешно обновлены", "success")
                return redirect(url_for("medicines"))
            except Exception as e:
                flash(f"Ошибка при обновлении данных препарата: {str(e)}", "error")
        
        return render_template("medicine_form.html", medicine=medicine)
    
    @app.route("/medicines/delete/<int:medicine_id>", methods=["POST"])
    def delete_medicine(medicine_id):
        """Удаление препарата."""
        medicine = Medicine.get_by_id(medicine_id)
        if medicine:
            try:
                medicine.delete()
                flash("Препарат успешно удалён", "success")
            except Exception as e:
                flash(f"Ошибка при удалении препарата: {str(e)}", "error")
        else:
            flash("Препарат не найден", "error")
        
        return redirect(url_for("medicines"))
    
    # Маршруты для назначений с пагинацией
    @app.route("/prescriptions")
    def prescriptions():
        """Страница списка назначений с пагинацией."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        patient_id = request.args.get('patient_id', type=int)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Prescription.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Prescription.get_paginated(page, per_page)
        
        # Получаем списки пациентов и препаратов для фильтров (ограниченное количество)
        patients = Patient.get_paginated(1, 50)['items']  # Первые 50 пациентов для выпадающего списка
        medicines = Medicine.get_paginated(1, 50)['items']  # Первые 50 препаратов для выпадающего списка
        
        return render_template("prescriptions_paginated.html", 
                             prescriptions=pagination_data['items'],
                             pagination=pagination_data,
                             patients=patients, 
                             medicines=medicines,
                             selected_patient_id=patient_id)
    
    @app.route("/prescriptions/add", methods=["GET", "POST"])
    def add_prescription():
        """Добавление нового назначения."""
        if request.method == "POST":
            try:
                patient_id = int(request.form["patient_id"])
                medicine_id = int(request.form["medicine_id"])
                daily_dose = float(request.form.get("daily_dose", 0)) if request.form.get("daily_dose") else None
                treatment_days = int(request.form.get("treatment_days", 0)) if request.form.get("treatment_days") else None
                quantity_packs = float(request.form["quantity_packs"])
                
                # Валидация
                is_valid, error_message = BusinessLogic.validate_prescription(
                    patient_id, medicine_id, quantity_packs
                )
                
                if not is_valid:
                    flash(error_message, "error")
                else:
                    prescription = Prescription(
                        patient_id=patient_id,
                        medicine_id=medicine_id,
                        prescription_date=request.form["prescription_date"],
                        quantity_packs=quantity_packs,
                        daily_dose=daily_dose,
                        treatment_days=treatment_days
                    )
                    prescription.save()
                    flash("Назначение успешно добавлено", "success")
                    return redirect(url_for("prescriptions"))
            except Exception as e:
                flash(f"Ошибка при добавлении назначения: {str(e)}", "error")
        
        # Получаем ограниченные списки для форм
        patients = Patient.get_paginated(1, 100)['items']
        medicines = Medicine.get_paginated(1, 100)['items']
        return render_template("prescription_form.html", patients=patients, medicines=medicines)
    
    @app.route("/prescriptions/edit/<int:prescription_id>", methods=["GET", "POST"])
    def edit_prescription(prescription_id):
        """Редактирование назначения."""
        prescription = Prescription.get_by_id(prescription_id)
        if not prescription:
            flash("Назначение не найдено", "error")
            return redirect(url_for("prescriptions"))
        
        if request.method == "POST":
            try:
                prescription.patient_id = int(request.form["patient_id"])
                prescription.medicine_id = int(request.form["medicine_id"])
                prescription.prescription_date = request.form["prescription_date"]
                prescription.quantity_packs = float(request.form["quantity_packs"])
                prescription.daily_dose = float(request.form.get("daily_dose", 0)) if request.form.get("daily_dose") else None
                prescription.treatment_days = int(request.form.get("treatment_days", 0)) if request.form.get("treatment_days") else None
                prescription.save()
                flash("Назначение успешно обновлено", "success")
                return redirect(url_for("prescriptions"))
            except Exception as e:
                flash(f"Ошибка при обновлении назначения: {str(e)}", "error")
        
        patients = Patient.get_paginated(1, 100)['items']
        medicines = Medicine.get_paginated(1, 100)['items']
        return render_template("prescription_form.html", prescription=prescription, patients=patients, medicines=medicines)

    @app.route("/prescriptions/delete/<int:prescription_id>", methods=["POST"])
    def delete_prescription(prescription_id):
        """Удаление назначения."""
        prescription = Prescription.get_by_id(prescription_id)
        if prescription:
            try:
                prescription.delete()
                flash("Назначение успешно удалено", "success")
            except Exception as e:
                flash(f"Ошибка при удалении назначения: {str(e)}", "error")
        else:
            flash("Назначение не найдено", "error")
        
        return redirect(url_for("prescriptions"))

    # Маршруты для выдач с пагинацией
    @app.route("/dispensings")
    def dispensings():
        """Страница списка выдач с пагинацией."""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        patient_id = request.args.get('patient_id', type=int)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Dispensing.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Dispensing.get_paginated(page, per_page)
        
        # Получаем списки пациентов и препаратов для фильтров (ограниченное количество)
        patients = Patient.get_paginated(1, 50)['items']
        medicines = Medicine.get_paginated(1, 50)['items']
        
        return render_template("dispensings_paginated.html", 
                             dispensings=pagination_data['items'],
                             pagination=pagination_data,
                             patients=patients, 
                             medicines=medicines,
                             selected_patient_id=patient_id)
    
    @app.route("/dispensings/add", methods=["GET", "POST"])
    def add_dispensing():
        """Добавление новой выдачи."""
        if request.method == "POST":
            try:
                patient_id = int(request.form["patient_id"])
                medicine_id = int(request.form["medicine_id"])
                quantity_packs = float(request.form["quantity_packs"])
                
                # Валидация
                is_valid, error_message = BusinessLogic.validate_dispensing(
                    patient_id, medicine_id, quantity_packs
                )
                
                if not is_valid:
                    flash(error_message, "error")
                else:
                    dispensing = Dispensing(
                        patient_id=patient_id,
                        medicine_id=medicine_id,
                        dispensing_date=request.form["dispensing_date"],
                        quantity_packs=quantity_packs
                    )
                    dispensing.save()
                    flash("Выдача успешно зарегистрирована", "success")
                    return redirect(url_for("dispensings"))
            except Exception as e:
                flash(f"Ошибка при регистрации выдачи: {str(e)}", "error")
        
        patients = Patient.get_paginated(1, 100)['items']
        medicines = Medicine.get_paginated(1, 100)['items']
        return render_template("dispensing_form.html", patients=patients, medicines=medicines)
    
    @app.route("/dispensings/edit/<int:dispensing_id>", methods=["GET", "POST"])
    def edit_dispensing(dispensing_id):
        """Редактирование выдачи."""
        dispensing = Dispensing.get_by_id(dispensing_id)
        if not dispensing:
            flash("Выдача не найдена", "error")
            return redirect(url_for("dispensings"))
        
        if request.method == "POST":
            try:
                dispensing.patient_id = int(request.form["patient_id"])
                dispensing.medicine_id = int(request.form["medicine_id"])
                dispensing.dispensing_date = request.form["dispensing_date"]
                dispensing.quantity_packs = float(request.form["quantity_packs"])
                dispensing.save()
                flash("Выдача успешно обновлена", "success")
                return redirect(url_for("dispensings"))
            except Exception as e:
                flash(f"Ошибка при обновлении выдачи: {str(e)}", "error")
        
        patients = Patient.get_paginated(1, 100)['items']
        medicines = Medicine.get_paginated(1, 100)['items']
        return render_template("dispensing_form.html", dispensing=dispensing, patients=patients, medicines=medicines)

    @app.route("/dispensings/delete/<int:dispensing_id>", methods=["POST"])
    def delete_dispensing(dispensing_id):
        """Удаление выдачи."""
        dispensing = Dispensing.get_by_id(dispensing_id)
        if dispensing:
            try:
                dispensing.delete()
                flash("Выдача успешно удалена", "success")
            except Exception as e:
                flash(f"Ошибка при удалении выдачи: {str(e)}", "error")
        else:
            flash("Выдача не найдена", "error")
        
        return redirect(url_for("dispensings"))

    # API маршруты для автозаполнения с пагинацией
    @app.route("/api/patients/search")
    def search_patients():
        """Поиск пациентов для автозаполнения с ограничением результатов."""
        query = request.args.get("q", "").strip()
        if len(query) < 2:
            return jsonify([])
        
        # Используем пагинацию для ограничения результатов
        result = Patient.search_paginated(query, 1, 10)
        
        filtered_patients = []
        for patient in result['items']:
            filtered_patients.append({
                "id": patient.patient_id,
                "text": f"{patient.fio} ({patient.diagnosis})",
                "fio": patient.fio,
                "diagnosis": patient.diagnosis
            })
        
        return jsonify(filtered_patients)
    
    @app.route("/api/medicines/search")
    def search_medicines():
        """Поиск препаратов для автозаполнения с ограничением результатов."""
        query = request.args.get("q", "").strip()
        if len(query) < 2:
            return jsonify([])
        
        # Используем пагинацию для ограничения результатов
        result = Medicine.search_paginated(query, 1, 10)
        
        filtered_medicines = []
        for medicine in result['items']:
            price_text = f" - {medicine.price} руб." if medicine.price else ""
            filtered_medicines.append({
                "id": medicine.medicine_id,
                "text": f"{medicine.trade_name_vk} ({medicine.standardized_mnn}){price_text}",
                "trade_name": medicine.trade_name_vk,
                "mnn": medicine.standardized_mnn,
                "price": medicine.price
            })
        
        return jsonify(filtered_medicines)

    # Маршруты для настройки пагинации
    @app.route("/settings/pagination", methods=["GET", "POST"])
    def pagination_settings():
        """Настройки пагинации."""
        if request.method == "POST":
            try:
                default_per_page = int(request.form.get("default_per_page", 10))
                max_per_page = int(request.form.get("max_per_page", 100))
                
                # Сохранение настроек в сессии или конфигурации
                from flask import session
                session['default_per_page'] = default_per_page
                session['max_per_page'] = max_per_page
                
                flash("Настройки пагинации успешно сохранены", "success")
            except Exception as e:
                flash(f"Ошибка при сохранении настроек: {str(e)}", "error")
        
        # Получение текущих настроек
        from flask import session
        current_settings = {
            'default_per_page': session.get('default_per_page', 10),
            'max_per_page': session.get('max_per_page', 100)
        }
        
        return render_template("pagination_settings.html", settings=current_settings)

    # Маршруты для массового импорта данных
    @app.route("/import/patients", methods=["GET", "POST"])
    def import_patients():
        """Массовый импорт пациентов из CSV."""
        if request.method == "POST":
            try:
                if 'file' not in request.files:
                    flash("Файл не выбран", "error")
                    return redirect(request.url)
                
                file = request.files['file']
                if file.filename == '':
                    flash("Файл не выбран", "error")
                    return redirect(request.url)
                
                if file and file.filename.endswith('.csv'):
                    import csv
                    import io
                    
                    # Чтение CSV файла
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.reader(stream)
                    
                    # Пропускаем заголовок
                    next(csv_input)
                    
                    patients_data = []
                    for row in csv_input:
                        if len(row) >= 4:  # fio, birth_year, diagnosis, attending_doctor
                            patients_data.append((row[0], int(row[1]), row[2], row[3]))
                    
                    # Массовая вставка
                    Patient.bulk_create(patients_data)
                    flash(f"Успешно импортировано {len(patients_data)} пациентов", "success")
                    
                else:
                    flash("Поддерживаются только CSV файлы", "error")
                    
            except Exception as e:
                flash(f"Ошибка при импорте: {str(e)}", "error")
        
        return render_template("import_patients.html")

    @app.route("/import/medicines", methods=["GET", "POST"])
    def import_medicines():
        """Массовый импорт препаратов из CSV."""
        if request.method == "POST":
            try:
                if 'file' not in request.files:
                    flash("Файл не выбран", "error")
                    return redirect(request.url)
                
                file = request.files['file']
                if file.filename == '':
                    flash("Файл не выбран", "error")
                    return redirect(request.url)
                
                if file and file.filename.endswith('.csv'):
                    import csv
                    import io
                    
                    # Чтение CSV файла
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_input = csv.reader(stream)
                    
                    # Пропускаем заголовок
                    next(csv_input)
                    
                    medicines_data = []
                    for row in csv_input:
                        if len(row) >= 9:  # все обязательные поля
                            price = float(row[8]) if row[8] and row[8] != 'н/д' else None
                            medicines_data.append((
                                row[0], row[1], row[2], row[3], row[4], 
                                row[5], row[6], row[7], price
                            ))
                    
                    # Массовая вставка
                    Medicine.bulk_create(medicines_data)
                    flash(f"Успешно импортировано {len(medicines_data)} препаратов", "success")
                    
                else:
                    flash("Поддерживаются только CSV файлы", "error")
                    
            except Exception as e:
                flash(f"Ошибка при импорте: {str(e)}", "error")
        
        return render_template("import_medicines.html")

    # Маршрут для экспорта данных
    @app.route("/export/<table_name>")
    def export_data(table_name):
        """Экспорт данных в CSV формате."""
        try:
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            if table_name == 'patients':
                # Экспорт всех пациентов
                patients = Patient.get_all()
                writer.writerow(['patient_id', 'fio', 'birth_year', 'diagnosis', 'attending_doctor'])
                for patient in patients:
                    writer.writerow([
                        patient.patient_id, patient.fio, patient.birth_year, 
                        patient.diagnosis, patient.attending_doctor
                    ])
                filename = 'patients.csv'
                
            elif table_name == 'medicines':
                # Экспорт всех препаратов
                medicines = Medicine.get_all()
                writer.writerow([
                    'medicine_id', 'smmn_node_code', 'section', 'standardized_mnn',
                    'trade_name_vk', 'standardized_dosage_form', 'standardized_dosage',
                    'characteristic', 'packaging', 'price'
                ])
                for medicine in medicines:
                    writer.writerow([
                        medicine.medicine_id, medicine.smmn_node_code, medicine.section,
                        medicine.standardized_mnn, medicine.trade_name_vk,
                        medicine.standardized_dosage_form, medicine.standardized_dosage,
                        medicine.characteristic, medicine.packaging, medicine.price
                    ])
                filename = 'medicines.csv'
                
            else:
                flash("Неподдерживаемая таблица для экспорта", "error")
                return redirect(url_for("index"))
            
            # Создание ответа с CSV файлом
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-type"] = "text/csv"
            
            return response
            
        except Exception as e:
            flash(f"Ошибка при экспорте: {str(e)}", "error")
            return redirect(url_for("index"))

