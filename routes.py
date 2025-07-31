from flask import render_template, request, redirect, url_for, flash, make_response
from models import Patient, Medicine, Prescription, Dispensing
from business_logic import BusinessLogic
from datetime import datetime

def init_routes(app):
    """Инициализация маршрутов Flask приложения."""
    
    @app.route("/")
    def index():
        """Главная страница."""
        return render_template("index.html")
    
    # Маршруты для пациентов
    @app.route("/patients")
    def patients():
        """Страница списка пациентов."""
        patients = Patient.get_all()
        return render_template("patients.html", patients=patients)
    
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
    
    # Маршруты для препаратов
    @app.route("/medicines")
    def medicines():
        """Страница списка препаратов."""
        medicines = Medicine.get_all()
        return render_template("medicines.html", medicines=medicines)
    
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
                    packaging=int(request.form["packaging"]),
                    price=float(request.form["price"])
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
                medicine.packaging = int(request.form["packaging"])
                medicine.price = float(request.form["price"])
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
    
    # Маршруты для назначений
    @app.route("/prescriptions")
    def prescriptions():
        """Страница списка назначений."""
        prescriptions = Prescription.get_all()
        patients = Patient.get_all()
        medicines = Medicine.get_all()
        return render_template("prescriptions.html", 
                             prescriptions=prescriptions, 
                             patients=patients, 
                             medicines=medicines)
    
    @app.route("/prescriptions/add", methods=["GET", "POST"])
    def add_prescription():
        """Добавление нового назначения."""
        if request.method == "POST":
            try:
                patient_id = int(request.form["patient_id"])
                medicine_id = int(request.form["medicine_id"])
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
                        quantity_packs=quantity_packs
                    )
                    prescription.save()
                    flash("Назначение успешно добавлено", "success")
                    return redirect(url_for("prescriptions"))
            except Exception as e:
                flash(f"Ошибка при добавлении назначения: {str(e)}", "error")
        
        patients = Patient.get_all()
        medicines = Medicine.get_all()
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
                prescription.save()
                flash("Назначение успешно обновлено", "success")
                return redirect(url_for("prescriptions"))
            except Exception as e:
                flash(f"Ошибка при обновлении назначения: {str(e)}", "error")
        
        patients = Patient.get_all()
        medicines = Medicine.get_all()
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

    # Маршруты для выдач
    @app.route("/dispensings")
    def dispensings():
        """Страница списка выдач."""
        dispensings = Dispensing.get_all()
        patients = Patient.get_all()
        medicines = Medicine.get_all()
        return render_template("dispensings.html", 
                             dispensings=dispensings, 
                             patients=patients, 
                             medicines=medicines)
    
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
        
        patients = Patient.get_all()
        medicines = Medicine.get_all()
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
        
        patients = Patient.get_all()
        medicines = Medicine.get_all()
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

    # Маршруты для отчётов
    @app.route("/reports")
    def reports():
        """Страница отчётов."""
        report = BusinessLogic.generate_medicine_report()
        stats = BusinessLogic.get_medicine_usage_statistics()
        return render_template("reports.html", report=report, stats=stats)
    
    @app.route("/reports/export/medicines")
    def export_medicine_report():
        """Экспорт отчёта по препаратам в CSV."""
        csv_content = BusinessLogic.export_medicine_report_to_csv()
        
        response = make_response(csv_content)
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = f"attachment; filename=medicine_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"
        
        return response
    
    @app.route("/reports/patient")
    def patient_report():
        """Отчёт по пациентам."""
        # Заглушка для будущей реализации
        flash("Отчёт по пациентам находится в разработке", "info")
        return redirect(url_for("reports"))
    
    @app.route("/reports/dispensing")
    def dispensing_report():
        """Отчёт по выдачам."""
        # Заглушка для будущей реализации
        flash("Отчёт по выдачам находится в разработке", "info")
        return redirect(url_for("reports"))
    
    @app.route("/reports/financial")
    def financial_report():
        """Финансовый отчёт."""
        # Заглушка для будущей реализации
        flash("Финансовый отчёт находится в разработке", "info")
        return redirect(url_for("reports"))
    
    # API маршруты для AJAX запросов
    @app.route("/api/patient/<int:patient_id>/remaining_need/<int:medicine_id>")
    def api_remaining_need(patient_id, medicine_id):
        """API для получения остаточной потребности пациента в препарате."""
        remaining_need = BusinessLogic.calculate_remaining_need(patient_id, medicine_id)
        return {"remaining_need": remaining_need}
    
    @app.route("/api/patient/<int:patient_id>/summary")
    def api_patient_summary(patient_id):
        """API для получения сводной информации по пациенту."""
        summary = BusinessLogic.get_patient_medicine_summary(patient_id)
        return {"summary": summary}
    
    return app

