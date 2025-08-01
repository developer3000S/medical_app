from flask import render_template, request, redirect, url_for, flash, make_response, jsonify
from models_updated import Patient, Medicine, Prescription, Dispensing
from business_logic import BusinessLogic
from datetime import datetime
import csv
import io

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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "", type=str)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if search:
            pagination_data = Patient.search_paginated(search, page, per_page)
        else:
            pagination_data = Patient.get_paginated(page, per_page)
        
        return render_template("patients_paginated.html", 
                             patients=pagination_data["items"],
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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "", type=str)
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if min_price is not None or max_price is not None:
            pagination_data = Medicine.get_by_price_range(min_price, max_price, page, per_page)
        elif search:
            pagination_data = Medicine.search_paginated(search, page, per_page)
        else:
            pagination_data = Medicine.get_paginated(page, per_page)
        
        return render_template("medicines_paginated.html", 
                             medicines=pagination_data["items"],
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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        patient_id = request.args.get("patient_id", type=int)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Prescription.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Prescription.get_paginated(page, per_page)
        
        # Получаем списки пациентов и препаратов для фильтров (ограниченное количество)
        patients = Patient.get_paginated(1, 50)["items"]  # Первые 50 пациентов для выпадающего списка
        medicines = Medicine.get_paginated(1, 50)["items"]  # Первые 50 препаратов для выпадающего списка
        
        return render_template("prescriptions_paginated.html", 
                             prescriptions=pagination_data["items"],
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
        patients = Patient.get_paginated(1, 100)["items"]
        medicines = Medicine.get_paginated(1, 100)["items"]
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
        
        patients = Patient.get_paginated(1, 100)["items"]
        medicines = Medicine.get_paginated(1, 100)["items"]
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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        patient_id = request.args.get("patient_id", type=int)
        
        # Ограничение количества записей на странице для производительности
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Dispensing.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Dispensing.get_paginated(page, per_page)
        
        # Получаем списки пациентов и препаратов для фильтров (ограниченное количество)
        patients = Patient.get_paginated(1, 50)["items"]
        medicines = Medicine.get_paginated(1, 50)["items"]
        
        return render_template("dispensings_paginated.html", 
                             dispensings=pagination_data["items"],
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
        
        patients = Patient.get_paginated(1, 100)["items"]
        medicines = Medicine.get_paginated(1, 100)["items"]
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
                flash("Данные выдачи успешно обновлены", "success")
                return redirect(url_for("dispensings"))
            except Exception as e:
                flash(f"Ошибка при обновлении данных выдачи: {str(e)}", "error")
        
        patients = Patient.get_paginated(1, 100)["items"]
        medicines = Medicine.get_paginated(1, 100)["items"]
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

    # Маршруты для отчетов и экспорта данных
    @app.route("/reports")
    def reports():
        """Страница отчетов."""
        return render_template("reports.html")

    @app.route("/export_data/<string:model_name>")
    def export_data(model_name):
        """Экспорт данных в CSV."""
        si = io.StringIO()
        cw = csv.writer(si)

        if model_name == "patients":
            headers = ["patient_id", "fio", "birth_year", "diagnosis", "attending_doctor", "created_at", "updated_at"]
            data = Patient.get_all()
        elif model_name == "medicines":
            headers = ["medicine_id", "smmn_node_code", "section", "standardized_mnn", "trade_name_vk", 
                       "standardized_dosage_form", "standardized_dosage", "characteristic", "packaging", 
                       "price", "created_at", "updated_at"]
            data = Medicine.get_all()
        elif model_name == "prescriptions":
            headers = ["prescription_id", "patient_id", "medicine_id", "prescription_date", 
                       "quantity_packs", "daily_dose", "treatment_days", "created_at", "updated_at"]
            data = Prescription.get_all()
        elif model_name == "dispensings":
            headers = ["dispensing_id", "patient_id", "medicine_id", "dispensing_date", 
                       "quantity_packs", "created_at", "updated_at"]
            data = Dispensing.get_all()
        else:
            flash("Неизвестный тип данных для экспорта", "error")
            return redirect(url_for("reports"))

        cw.writerow(headers)
        for row in data:
            cw.writerow([getattr(row, col) for col in headers])

        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = f"attachment; filename={model_name}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    @app.route("/api/patients")
    def api_patients():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "", type=str)
        
        per_page = min(per_page, 100)
        
        if search:
            pagination_data = Patient.search_paginated(search, page, per_page)
        else:
            pagination_data = Patient.get_paginated(page, per_page)
        
        # Преобразование объектов Patient в словари для JSON сериализации
        patients_data = [
            {
                "patient_id": p.patient_id,
                "fio": p.fio,
                "birth_year": p.birth_year,
                "diagnosis": p.diagnosis,
                "attending_doctor": p.attending_doctor,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            } for p in pagination_data["items"]
        ]
        
        return jsonify({
            "items": patients_data,
            "total_pages": pagination_data["total_pages"],
            "total_items": pagination_data["total_items"],
            "current_page": pagination_data["current_page"],
            "per_page": pagination_data["per_page"]
        })

    @app.route("/api/medicines")
    def api_medicines():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", "", type=str)
        min_price = request.args.get("min_price", type=float)
        max_price = request.args.get("max_price", type=float)
        
        per_page = min(per_page, 100)
        
        if min_price is not None or max_price is not None:
            pagination_data = Medicine.get_by_price_range(min_price, max_price, page, per_page)
        elif search:
            pagination_data = Medicine.search_paginated(search, page, per_page)
        else:
            pagination_data = Medicine.get_paginated(page, per_page)
        
        medicines_data = [
            {
                "medicine_id": m.medicine_id,
                "smmn_node_code": m.smmn_node_code,
                "section": m.section,
                "standardized_mnn": m.standardized_mnn,
                "trade_name_vk": m.trade_name_vk,
                "standardized_dosage_form": m.standardized_dosage_form,
                "standardized_dosage": m.standardized_dosage,
                "characteristic": m.characteristic,
                "packaging": m.packaging,
                "price": m.price,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None
            } for m in pagination_data["items"]
        ]
        
        return jsonify({
            "items": medicines_data,
            "total_pages": pagination_data["total_pages"],
            "total_items": pagination_data["total_items"],
            "current_page": pagination_data["current_page"],
            "per_page": pagination_data["per_page"]
        })

    @app.route("/api/prescriptions")
    def api_prescriptions():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        patient_id = request.args.get("patient_id", type=int)
        
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Prescription.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Prescription.get_paginated(page, per_page)
        
        prescriptions_data = [
            {
                "prescription_id": p.prescription_id,
                "patient_id": p.patient_id,
                "medicine_id": p.medicine_id,
                "prescription_date": p.prescription_date.isoformat() if p.prescription_date else None,
                "quantity_packs": p.quantity_packs,
                "daily_dose": p.daily_dose,
                "treatment_days": p.treatment_days,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            } for p in pagination_data["items"]
        ]
        
        return jsonify({
            "items": prescriptions_data,
            "total_pages": pagination_data["total_pages"],
            "total_items": pagination_data["total_items"],
            "current_page": pagination_data["current_page"],
            "per_page": pagination_data["per_page"]
        })

    @app.route("/api/dispensings")
    def api_dispensings():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        patient_id = request.args.get("patient_id", type=int)
        
        per_page = min(per_page, 100)
        
        if patient_id:
            pagination_data = Dispensing.get_by_patient_paginated(patient_id, page, per_page)
        else:
            pagination_data = Dispensing.get_paginated(page, per_page)
        
        dispensings_data = [
            {
                "dispensing_id": d.dispensing_id,
                "patient_id": d.patient_id,
                "medicine_id": d.medicine_id,
                "dispensing_date": d.dispensing_date.isoformat() if d.dispensing_date else None,
                "quantity_packs": d.quantity_packs,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None
            } for d in pagination_data["items"]
        ]
        
        return jsonify({
            "items": dispensings_data,
            "total_pages": pagination_data["total_pages"],
            "total_items": pagination_data["total_items"],
            "current_page": pagination_data["current_page"],
            "per_page": pagination_data["per_page"]
        })



