from flask import Flask
import config
from database_updated import init_db, close_db, insert_sample_data, create_indexes_for_performance
from routes_updated import init_routes

app = Flask(__name__)
app.config.from_object(config)

# Инициализация маршрутов с поддержкой пагинации
# Маршруты должны быть инициализированы до первого запроса
# или до использования url_for в шаблонах.
init_routes(app)

# Инициализация базы данных при запуске
with app.app_context():
    init_db()
    insert_sample_data()
    create_indexes_for_performance()  # Создание дополнительных индексов для производительности

# Закрытие соединения с БД после каждого запроса
app.teardown_appcontext(close_db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


