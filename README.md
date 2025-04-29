# Веб-приложение для управления спортом

Комплексное веб-приложение для управления спортивными данными, включая команды, игроков, тренеров, матчи и болельщиков.

## Функции

- **Управление командами**: Добавление, редактирование и удаление спортивных команд
- **Управление игроками**: Управление игроками и их назначение в команды
- **Управление тренерами**: Отслеживание тренеров и их опыта
- **Управление матчами**: Планирование и организация спортивных матчей
- **Управление болельщиками**: Ведение базы данных зарегистрированных болельщиков

## Схема базы данных

Приложение использует следующую схему базы данных:

### Таблица команд (Teams Table)
| Поле | Тип | Описание |
|------|-----|----------|
| team_id | INT | Первичный ключ |
| team_name | VARCHAR | Название команды |

### Таблица игроков (Players Table)
| Поле | Тип | Описание |
|------|-----|----------|
| player_id | INT | Первичный ключ |
| first_name | VARCHAR | Имя игрока |
| last_name | VARCHAR | Фамилия игрока |
| birth_date | DATE | Дата рождения |
| position | VARCHAR | Позиция игрока |
| team_id | INT | Внешний ключ к команде |

### Таблица тренеров (Coaches Table)
| Поле | Тип | Описание |
|------|-----|----------|
| coach_id | INT | Первичный ключ |
| first_name | VARCHAR | Имя тренера |
| last_name | VARCHAR | Фамилия тренера |
| birth_date | DATE | Дата рождения |
| experience_years | SMALLINT | Годы тренерского опыта |

### Таблица матчей (Matches Table)
| Поле | Тип | Описание |
|------|-----|----------|
| match_id | INT | Первичный ключ |
| match_date | DATETIME | Дата и время матча |
| tournament | VARCHAR | Название турнира или соревнования |

### Таблица болельщиков (Fans Table)
| Поле | Тип | Описание |
|------|-----|----------|
| fan_id | INT | Первичный ключ |
| first_name | VARCHAR | Имя болельщика |
| last_name | VARCHAR | Фамилия болельщика |
| email | VARCHAR | Адрес электронной почты |
| phone | VARCHAR | Контактный номер телефона |
| registration_date | DATETIME | Дата и время регистрации |

## Установка

1. Клонируйте этот репозиторий
```bash
git clone https://github.com/yourusername/sports-management-app.git
cd sports-management-app

python -m venv venv
# На Windows
venv\Scripts\activate
# На macOS/Linux
source venv/bin/activate
pip install -r requirements.txt

python [app.py](http://_vscodecontentref_/0)

sports-management-app/
├── [app.py](http://_vscodecontentref_/1)                  # Основной файл приложения
├── requirements.txt        # Зависимости Python
├── README.md               # Документация
└── templates/              # HTML-шаблоны
    ├── base.html           # Базовый шаблон с общими элементами
    ├── home.html           # Шаблон главной страницы
    ├── teams/              # Шаблоны, связанные с командами
    ├── players/            # Шаблоны, связанные с игроками
    ├── coaches/            # Шаблоны, связанные с тренерами
    ├── matches/            # Шаблоны, связанные с матчами
    └── fans/               # Шаблоны, связанные с болельщиками

Технологический стек
Backend: Python, Flask
База данных: SQLAlchemy с SQLite
Frontend: HTML, Bootstrap 5
Разработка: Werkzeug development server