# Vocab Punk — Сервис словарей

Веб-приложение для управления и публикации словарей, поддерживающее:
- Добавление, редактирование и удаление слов
- Импорт слов из JSON-файлов
- Публикацию словарей в виде отдельных файлов
- Авторизацию через JWT
- Управление правами пользователей (админ / обычный)

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/vocab-punk.git
cd vocab-punk
```

### 2. Создание виртуального окружения и установка зависимостей
```bash
python -m venv venv
source venv/bin/activate   # для macOS/Linux
venv\Scripts\activate      # для Windows

pip install -r requirements.txt
```

### 3. Настройка конфигурации
Все базы данных и словари хранятся в папке `data/`.

По умолчанию конфигурация задаётся в `config.py`:
```python
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_DB_PATH = os.path.join(DATA_DIR, "users.db")
DICTS_DB_PATH = os.path.join(DATA_DIR, "dictionaries.db")
DICTIONARIES_DIR = os.path.join(DICTIONARIES_DIR, "dictionaries")
```

Если нужно, можно переопределить эти пути через переменные окружения:
```bash
export USERS_DB_PATH=/path/to/users.db
export DICTS_DB_PATH=/path/to/dictionaries.db
export DICTIONARIES_DIR=/path/to/dictionaries
```

### 4. Инициализация базы данных
```bash
flask db upgrade
```

### 5. Запуск приложения
```bash
flask run
```
По умолчанию сервер запустится на `http://127.0.0.1:3000`.

---

## 📂 Структура проекта
```
vocab-punk/
│
├── app/                     # Основное приложение Flask
│   ├── models/            # SQLAlchemy модели
│   ├── routes/              # Роуты приложения
│   ├── templates/           # HTML-шаблоны
│   └── static/              # CSS, JS, изображения
│
├── data/                    # Хранилище данных (создаётся автоматически)
│   ├── users.db             # БД пользователей
│   ├── dictionaries.db      # БД словарей
│   └── dictionaries/        # Папка для опубликованных словарей
│
├── config.py                # Конфигурация приложения
├── requirements.txt         # Зависимости
├── README.md                # Документация
└── run.py                   # Точка входа
```

---

## 📦 Импорт слов из JSON
Формат поддерживаемого файла:
```json
[
  {
    "id": "b1_0001",
    "englishWord": "acquire",
    "englishIPA": "əˈkwaɪər",
    "englishIPAru": "эквайэр",
    "russianWord": "приобретать",
    "russianIPA": "[prʲɪɐbrʲɪˈtatʲ]",
    "russianIPAen": "priobretat",
    "level": "B1"
  }
]
```
Импорт выполняется через интерфейс словаря — выберите файл и загрузите.

---

## 🔑 Авторизация
Используется JWT.  
Для запросов к API токен не требуется.

---

## 📜 Лицензия
MIT License
