import os

# Секретный ключ для сессий и CSRF-защиты
SECRET_KEY = 'your-secret-key-here-change-in-production'

# Путь к базе данных SQLite
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'medical_app.db')

# Настройки Flask
DEBUG = True
TESTING = False

# Настройки для работы с формами
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# Настройки для загрузки файлов
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB максимальный размер файла

# Настройки для отчётов
REPORTS_EXPORT_FORMAT = 'csv'
REPORTS_DATE_FORMAT = '%Y-%m-%d'

