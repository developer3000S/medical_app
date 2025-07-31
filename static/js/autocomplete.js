/**
 * Модуль автозаполнения для полей выбора пациентов и препаратов
 */

class AutoComplete {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            minLength: 2,
            delay: 300,
            maxResults: 10,
            searchUrl: '',
            onSelect: null,
            placeholder: 'Начните вводить для поиска...',
            ...options
        };
        
        this.dropdown = null;
        this.searchTimeout = null;
        this.selectedIndex = -1;
        this.results = [];
        
        this.init();
    }
    
    init() {
        // Создаем контейнер для выпадающего списка
        this.createDropdown();
        
        // Добавляем обработчики событий
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('focus', this.handleFocus.bind(this));
        this.input.addEventListener('blur', this.handleBlur.bind(this));
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        
        // Устанавливаем placeholder
        this.input.placeholder = this.options.placeholder;
        
        // Скрываем оригинальный select если он есть
        const originalSelect = this.input.nextElementSibling;
        if (originalSelect && originalSelect.tagName === 'SELECT') {
            originalSelect.style.display = 'none';
        }
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ced4da;
            border-top: none;
            border-radius: 0 0 0.375rem 0.375rem;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        `;
        
        // Создаем wrapper для позиционирования
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.width = '100%';
        
        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
        wrapper.appendChild(this.dropdown);
    }
    
    handleInput(e) {
        const query = e.target.value.trim();
        
        if (query.length < this.options.minLength) {
            this.hideDropdown();
            return;
        }
        
        // Очищаем предыдущий таймер
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Устанавливаем новый таймер для задержки поиска
        this.searchTimeout = setTimeout(() => {
            this.search(query);
        }, this.options.delay);
    }
    
    handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= this.options.minLength) {
            this.search(query);
        }
    }
    
    handleBlur(e) {
        // Задержка для обработки клика по элементу списка
        setTimeout(() => {
            this.hideDropdown();
        }, 150);
    }
    
    handleKeydown(e) {
        if (!this.dropdown.style.display || this.dropdown.style.display === 'none') {
            return;
        }
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectNext();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectPrevious();
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.results[this.selectedIndex]) {
                    this.selectItem(this.results[this.selectedIndex]);
                }
                break;
            case 'Escape':
                this.hideDropdown();
                break;
        }
    }
    
    async search(query) {
        try {
            const response = await fetch(`${this.options.searchUrl}?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            this.results = results;
            this.showResults(results);
        } catch (error) {
            console.error('Ошибка поиска:', error);
            this.hideDropdown();
        }
    }
    
    showResults(results) {
        if (results.length === 0) {
            this.hideDropdown();
            return;
        }
        
        this.dropdown.innerHTML = '';
        this.selectedIndex = -1;
        
        results.forEach((item, index) => {
            const element = document.createElement('div');
            element.className = 'autocomplete-item';
            element.style.cssText = `
                padding: 8px 12px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
            `;
            element.textContent = item.text;
            
            element.addEventListener('mouseenter', () => {
                this.highlightItem(index);
            });
            
            element.addEventListener('click', () => {
                this.selectItem(item);
            });
            
            this.dropdown.appendChild(element);
        });
        
        this.showDropdown();
    }
    
    highlightItem(index) {
        // Убираем выделение с предыдущего элемента
        if (this.selectedIndex >= 0) {
            const prevItem = this.dropdown.children[this.selectedIndex];
            if (prevItem) {
                prevItem.style.backgroundColor = '';
            }
        }
        
        // Выделяем новый элемент
        this.selectedIndex = index;
        if (this.selectedIndex >= 0) {
            const item = this.dropdown.children[this.selectedIndex];
            if (item) {
                item.style.backgroundColor = '#e9ecef';
            }
        }
    }
    
    selectNext() {
        const nextIndex = this.selectedIndex + 1;
        if (nextIndex < this.results.length) {
            this.highlightItem(nextIndex);
        }
    }
    
    selectPrevious() {
        const prevIndex = this.selectedIndex - 1;
        if (prevIndex >= 0) {
            this.highlightItem(prevIndex);
        }
    }
    
    selectItem(item) {
        this.input.value = item.text;
        this.hideDropdown();
        
        // Вызываем callback если он задан
        if (this.options.onSelect) {
            this.options.onSelect(item);
        }
        
        // Обновляем скрытый select если он есть
        const originalSelect = this.input.parentNode.querySelector('select[style*="display: none"]');
        if (originalSelect) {
            originalSelect.value = item.id;
            
            // Создаем событие change для select
            const changeEvent = new Event('change', { bubbles: true });
            originalSelect.dispatchEvent(changeEvent);
        }
    }
    
    showDropdown() {
        this.dropdown.style.display = 'block';
    }
    
    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
    }
    
    // Метод для программной установки значения
    setValue(id, text) {
        this.input.value = text;
        
        const originalSelect = this.input.parentNode.querySelector('select[style*="display: none"]');
        if (originalSelect) {
            originalSelect.value = id;
        }
    }
}

// Функция для инициализации автозаполнения пациентов
function initPatientAutocomplete(inputElement, onSelectCallback) {
    return new AutoComplete(inputElement, {
        searchUrl: '/api/patients/search',
        placeholder: 'Начните вводить ФИО или диагноз пациента...',
        onSelect: onSelectCallback
    });
}

// Функция для инициализации автозаполнения препаратов
function initMedicineAutocomplete(inputElement, onSelectCallback) {
    return new AutoComplete(inputElement, {
        searchUrl: '/api/medicines/search',
        placeholder: 'Начните вводить название препарата...',
        onSelect: onSelectCallback
    });
}

// Экспортируем для использования в других скриптах
window.AutoComplete = AutoComplete;
window.initPatientAutocomplete = initPatientAutocomplete;
window.initMedicineAutocomplete = initMedicineAutocomplete;

