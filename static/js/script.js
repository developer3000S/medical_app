// Основной JavaScript файл для медицинской информационной системы

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeTableSorting();
    
    // Добавление анимации появления для карточек
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

// Инициализация подсказок Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Автоматическое скрытие алертов
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

// Валидация форм
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Сортировка таблиц
function initializeTableSorting() {
    const tables = document.querySelectorAll('table.sortable');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, header));
        });
    });
}

// Функция сортировки таблицы
function sortTable(table, header) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const sortType = header.dataset.sort;
    const isAscending = !header.classList.contains('sort-asc');
    
    // Удаление предыдущих классов сортировки
    header.parentNode.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Добавление нового класса сортировки
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    
    // Сортировка строк
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        let comparison = 0;
        
        if (sortType === 'number') {
            comparison = parseFloat(aValue) - parseFloat(bValue);
        } else if (sortType === 'date') {
            comparison = new Date(aValue) - new Date(bValue);
        } else {
            comparison = aValue.localeCompare(bValue, 'ru');
        }
        
        return isAscending ? comparison : -comparison;
    });
    
    // Обновление таблицы
    rows.forEach(row => tbody.appendChild(row));
}

// Функции для работы с формами
function validateRequired(input) {
    const value = input.value.trim();
    if (value === '') {
        showFieldError(input, 'Это поле обязательно для заполнения');
        return false;
    }
    clearFieldError(input);
    return true;
}

function validateEmail(input) {
    const email = input.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (email && !emailRegex.test(email)) {
        showFieldError(input, 'Введите корректный email адрес');
        return false;
    }
    clearFieldError(input);
    return true;
}

function validateNumber(input, min = null, max = null) {
    const value = parseFloat(input.value);
    if (isNaN(value)) {
        showFieldError(input, 'Введите корректное число');
        return false;
    }
    if (min !== null && value < min) {
        showFieldError(input, `Значение должно быть не менее ${min}`);
        return false;
    }
    if (max !== null && value > max) {
        showFieldError(input, `Значение должно быть не более ${max}`);
        return false;
    }
    clearFieldError(input);
    return true;
}

function showFieldError(input, message) {
    input.classList.add('is-invalid');
    let feedback = input.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearFieldError(input) {
    input.classList.remove('is-invalid');
    const feedback = input.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }
}

// Функции для работы с таблицами
function highlightTableRow(row) {
    row.style.backgroundColor = '#fff3cd';
    setTimeout(() => {
        row.style.backgroundColor = '';
    }, 2000);
}

function showTableLoading(table) {
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="100%" class="text-center py-4">
                <div class="loading"></div>
                <span class="ms-2">Загрузка данных...</span>
            </td>
        </tr>
    `;
}

function showTableEmpty(table, message = 'Нет данных для отображения') {
    const tbody = table.querySelector('tbody');
    const columnCount = table.querySelector('thead tr').children.length;
    tbody.innerHTML = `
        <tr>
            <td colspan="${columnCount}" class="text-center py-4 text-muted">
                <i class="fas fa-info-circle"></i>
                <span class="ms-2">${message}</span>
            </td>
        </tr>
    `;
}

// Функции для работы с модальными окнами
function showConfirmDialog(title, message, onConfirm, onCancel = null) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                    <button type="button" class="btn btn-primary confirm-btn">Подтвердить</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    
    modal.querySelector('.confirm-btn').addEventListener('click', () => {
        bsModal.hide();
        if (onConfirm) onConfirm();
    });
    
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
        if (onCancel) onCancel();
    });
    
    bsModal.show();
}

// Функции для работы с уведомлениями
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = `alert-${type}`;
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    if (duration > 0) {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

// Функции для работы с датами
function formatDate(date, format = 'dd.mm.yyyy') {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    switch (format) {
        case 'dd.mm.yyyy':
            return `${day}.${month}.${year}`;
        case 'yyyy-mm-dd':
            return `${year}-${month}-${day}`;
        case 'dd/mm/yyyy':
            return `${day}/${month}/${year}`;
        default:
            return date.toLocaleDateString('ru-RU');
    }
}

function parseDate(dateString) {
    // Поддержка различных форматов дат
    const formats = [
        /^(\d{2})\.(\d{2})\.(\d{4})$/, // dd.mm.yyyy
        /^(\d{4})-(\d{2})-(\d{2})$/, // yyyy-mm-dd
        /^(\d{2})\/(\d{2})\/(\d{4})$/ // dd/mm/yyyy
    ];
    
    for (const format of formats) {
        const match = dateString.match(format);
        if (match) {
            if (format === formats[1]) { // yyyy-mm-dd
                return new Date(match[1], match[2] - 1, match[3]);
            } else { // dd.mm.yyyy или dd/mm/yyyy
                return new Date(match[3], match[2] - 1, match[1]);
            }
        }
    }
    
    return new Date(dateString);
}

// Функции для работы с числами
function formatNumber(number, decimals = 2) {
    return Number(number).toLocaleString('ru-RU', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function formatCurrency(amount, currency = 'RUB') {
    return Number(amount).toLocaleString('ru-RU', {
        style: 'currency',
        currency: currency
    });
}

// Экспорт функций для использования в других файлах
window.MedicalApp = {
    validateRequired,
    validateEmail,
    validateNumber,
    showFieldError,
    clearFieldError,
    highlightTableRow,
    showTableLoading,
    showTableEmpty,
    showConfirmDialog,
    showNotification,
    formatDate,
    parseDate,
    formatNumber,
    formatCurrency
};

