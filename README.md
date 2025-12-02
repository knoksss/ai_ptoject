![our team](https://badgen.net/badge/cloring/web/red?icon=github)

![python](https://badgen.net/pypi/python/black) ![Flask](https://img.shields.io/badge/Flask-3.1-green) ![Docker](https://img.shields.io/badge/Docker-Ready-blue) ![AI](https://img.shields.io/badge/AI-LLaVA%2FMoondream-purple)

# Проект CLORING
![cloring-1](https://github.com/user-attachments/assets/399bea5a-77e9-4755-b4f3-ef154fd9bfc9)
**«CLORING»** - онлайн-платформа, где можно жертвовать или обмениваться одеждой. Её цель - *создать систему повторного использования текстиля*. Она поддерживает людей в трудных жизненных ситуациях, предоставляя им качественную одежду, нуждающиеся смогут получить помощь в приобретении одежды на безвозмездной основе, а также обменять неиспользуемую одежду на необходимую. Это улучшает их жизнь, давая возможность чувствовать себя уверенно и достойно без затрат на покупку новых вещей. *Проект является актуальным в данное время, так как проблема социального неравенства и материальной необеспеченности остаётся одной из наиболее значимых в современном обществе.* Проект выполнен в рамках предмета «Обучение слежением».
![cloring-2](https://github.com/user-attachments/assets/d7a824f6-07f6-41b8-a180-a441d8e55886)

## Основные функции

| Функция | Описание |
|---------|----------|
| **Обмен одеждой** | Выкладывайте свои вещи и обменивайте на вещи других пользователей |
| **Пожертвование** | Передавайте одежду малообеспеченным гражданам и получайте купоны |
| **AI-анализ** | Автоматическое распознавание категории, цвета и материала по фотографии |
| **Каталог** | Удобный просмотр доступных для обмена вещей с фото и описанием |
| **Личный кабинет** | Управление добавленными вещами и просмотр информации |

---

## Технологии

- **Backend:** Flask 3.1, Python 3.11
- **Database:** SQLite
- **AI:** Ollama (LLaVA / Moondream)
- **Frontend:** HTML, CSS, JavaScript
- **Развртнывание:** Docker, Docker Compose

---

## Структура проекта
```
CLORING-WEB/
├── src/                                  
│   ├── run.py                            # Главный файл
│   ├── db.py                             # Работа с базой данных SQLite
│   ├── validation.py                     # Валидация данных
│   ├── registration.py                   # Регистрация пользователей
│   ├── autotentification.py              # Аутентификация
│   ├── passwords.py                      # Хеширование паролей
│   ├── vlm_analyzer.py                   # AI-анализ изображений
│   ├── logger.py                         # Настройка логирования
│   └── constants.py                      # Константы и конфигурация
│
├── templates/                            
│   ├── main.html                         # Главная страница
│   ├── registration.html                 # Регистрация
│   ├── sign_in.html                      # Вход
│   ├── user_account.html                 # Личный кабинет
│   ├── upload_form.html                  # Форма добавления одежды
│   ├── catalog.html                      # Каталог вещей
│   ├── card.html                         # Карточка товара
│   ├── donation_form.html                # Форма пожертвования
│   ├── after_donation.html               # Страница после пожертвования
│   └── about.html                        # О проекте
│
├── tests/                                # Тесты
│   ├── test_valid_email.py
│   ├── test_valid_phone_number.py
│   ├── test_valid_clothes_name.py
│   ├── test_valid_clothes_brand.py
│   ├── test_valid_clothes_color.py
│   ├── test_valid_clothes_material.py
│   └── test_valid_clothes_description.py
│
├── static/                               
│   └── uploads/                          # Загруженные фото
│
├── data/                                 
│   └── database.db                       # База данных SQLite
│
├── Dockerfile                            # Docker-образ
├── docker-compose.yml                    # Docker Compose конфигурация
├── requirements.txt                      # Python зависимости
└── README.md                             # Описание проекта
```
---
## Команда проекта
[Панарин Максим](https://github.com/Bezriska) - **Тимлид**. Отвечает за общее руководство проектом, координацию работы ко-манды, распределение задач, контроль сроков выполнения, организацию со-вещаний и коммуникацию между участниками.

[Малинин Ярослав](https://github.com/collhoun) - **Backend-разработчик**. Отвечает за разработку серверной части приложения, проектирование и реализацию архитектуры базы данных, создание API, обес-печение безопасности данных, хеширование паролей и интеграцию фронтенд- и бэкенд-компонентов системы.

[Китаева Дарья](https://github.com/knoksss) - **Frontend-разработчик**. Отвечает за разработку клиентской части веб-приложения, создание пользовательского интерфейса на основе дизайн-макетов, верстку страниц на HTML/CSS, реализацию адаптивного дизайна.

[Галанова Екатерина](https://github.com/galanovaxxx) - **Аналитик**. Проводит исследование целевой аудитории и анализ рынка, изуча-ет статистические данные и потребности пользователей.

[Иващенко Юлия](https://github.com/jurolli) - **Frontend-разработчик**. Специализируется на реализации интерактивных эле-ментов интерфейса, разработке системы фильтрации в каталоге товаров. 










# CLORING-WEB
![my badge](https://badgen.net/badge/cloring/web/red?icon=github)

Веб-приложение для обмена и донации одежды с AI-анализом фотографий (BLIP).

![our team](https://badgen.net/badge/cloring/web/red?icon=github)

![python](https://badgen.net/pypi/python/black) ![Flask](https://img.shields.io/badge/Flask-3.1-green) ![Docker](https://img.shields.io/badge/Docker-Ready-blue) ![AI](https://img.shields.io/badge/AI-LLaVA%2FMoondream-purple)
# Проект CLORING
![cloring-1](https://github.com/user-attachments/assets/399bea5a-77e9-4755-b4f3-ef154fd9bfc9)
**«CLORING»** - онлайн-платформа, где можно жертвовать или обмениваться одеждой. Её цель - *создать систему повторного использования текстиля*. Она поддерживает людей в трудных жизненных ситуациях, предоставляя им качественную одежду, нуждающиеся смогут получить помощь в приобретении одежды на безвозмездной основе, а также обменять неиспользуемую одежду на необходимую. Это улучшает их жизнь, давая возможность чувствовать себя уверенно и достойно без затрат на покупку новых вещей. *Проект является актуальным в данное время, так как проблема социального неравенства и материальной необеспеченности остаётся одной из наиболее значимых в современном обществе.* Проект выполнен в рамках предмета «Обучение слежением».
![cloring-2](https://github.com/user-attachments/assets/d7a824f6-07f6-41b8-a180-a441d8e55886)


## Предварительные требования
- Python 3.11
- pip

## Установка
### Клонирование репозитория:
```
git clone https://github.com/
cd папка
```

## Основные функции
1. Обмен одеждой
2. Пожертвование одежды

## Структура проекта
```
CLORING-WEB/
├── src/                                  
│   └── autotification.py                   #
│   └── constants.py                        #
│   └── db.py                               #
│   └── logger.py                           #
│   └── passwords.py                        #
│   └── registation.py                      #
│   └── run.py                              #
│   └── validation.py                       #
├── templates/
│   └── abount.html                         # Страница "О нас"
│   └── after_donation.html                 # Страница, открывающаяся после пожертвования
│   └── card.html                           # Карточка товара
│   └── catalog.html                        # Каталог товаров
│   └── donation_form.html                  # Страница с пожертвованием одежды
│   └── main.html                           # Главная страница
│   └── registration.html                   # Форма регистрации
│   └── sign_in.html                        # Страница со входом
│   └── upload_form.html                    # Формы для отправки одежды
│   └── user_account.html                   # Аккаунт
├── tests/
│   └── test_valid_clothes_brand.py         # Тесты для проверки, насколько правильно
│   └── test_valid_clothes_color.py         # работают те или иные функции
│   └── test_valid_clothes_description.py
│   └── test_valid_clothes_material.py
│   └── test_valid_clothes_name.py
│   └── test_valid_email.py
│   └── test_valid_phone_number.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md                               # Описание проекта
├── docker-compose.yalm
└── requirements.txt                        # Зависимости Python
```






## Быстрый запуск в Docker

```bash
docker run -d -p 5000:5000 galanovaxxx/cloring-web:latest
```

Откройте http://localhost:5000

**Важно:** При первой загрузке фото модель BLIP скачается (~900 МБ, займет 1-2 минуты). Затем работает локально без интернета.

## Возможности
- Регистрация и каталог одежды
- Автоматический AI-анализ фото (категория, цвет, материал, состояние)

## Для разработки

```bash
docker-compose up -d
```

## Технологии
Flask, PyTorch, BLIP (Salesforce), Docker

