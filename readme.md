### Dashboard Finance

Управляйте своими финансами с легкостью с помощью Dashboard Finance — веб-приложения на основе Django.

### Описание:

__Dashboard Finance позволяет пользователям эффективно управлять своими финансами и получать представление о своих расходах и моделях инвестиций. Пользователи могут создавать несколько портфелей, каждый из которых связан с определенными валютами и типами счетов. Приложение поддерживает отслеживание транзакций в разных валютах, с конвертацией валют в режиме реального времени на основе последних курсов валют__.

#### Функции

    Аутентификация пользователя:
    вход/регистрация...

    Управление портфелем:
    Создавайте, редактируйте и удаляйте портфели...

    Отслеживание транзакций:
    Регистрируйте доходы, расходы и финансовые операции...
    
    Конвертация валюты:
    Динамическое обновление валютного баланса на основе обменных курсов...

#### Технологии

    Бэкенд: Django, SQLite...
    Фронтенд: HTML, CSS, JavaScript...
    Аутентификация: Система аутентификации Django...
    Внешние API: Используется для обменных курсов валют в режиме    реального времени...
    Библиотеки: BeautifulSoup для веб-скрейпинга...

#### Python

Установите Python версии 3.11.4

#### Env

Создайте виртуальную среду и активируйте ее.

#### Зависмости

Установите все зависмости из файла requirements.txt

#### Выполните миграцию

python manage.py migrate

#### Создаем суперпользователя

python manage.py createsuperuser

#### Запускаем приложение в Терминале 

python manage.py runserver
