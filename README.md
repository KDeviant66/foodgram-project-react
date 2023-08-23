ip: 158.160.78.31

login : anastas.93@mail.ru

password: Deviant66


Foodgram - это сайт для обмена рецептами. 

Возможности для пользователя:

- Публиковать свои любимые рецепты
- Просматривать рецепты других пользователей 
- Добавлять любимые рецепты в избранное
- Подписываться на других пользователей
- Составлять свой список покупок с ингредиентами понравившегося рецепта

Подготовка к запуску
На сервере создайте папку проекта - foodgram и скопируйте в нее файл docker-compose.production.yml.

В папке с проектом создайте файл .env и заполните его своими данными:

POSTGRES_ON - True для работы с БД PostgreSQL | False для работы с БД SQLite

POSTGRES_USER - имя пользователя для доступа к базе данных

POSTGRES_PASSWORD - пароль для доступа к базе данных

POSTGRES_DB - имя базы данных

SECRET_KEY - секретный ключ для Django

DEBUG - True/False - режим отладки Django

ALLOWED_HOSTS - список разрешенных хостов

DB_HOST - имя хоста базы данных

DB_PORT - порт базы данных

Запуск проекта:

Находясь в папке с проектом скачайте образы и запустите проект командами:
sudo docker compose -f docker-compose.production.yml up -d

Выполните миграции, соберите статические файлы бэкенда:

sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend mkdir -p backend_static/static/

sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic


Создайте суперпользователя:

sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
