from flask import Flask
import config
from database import init_db, close_db, insert_sample_data
from routes import init_routes

app = Flask(__name__)
app.config.from_object(config)

# Инициализация базы данных при запуске
with app.app_context():
    init_db()
    insert_sample_data()

# Закрытие соединения с БД после каждого запроса
app.teardown_appcontext(close_db)

# Инициализация маршрутов
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

