**domen**: kdeviant.sytes.net


**login** : anastas.93@mail.ru


**password**: Deviant66



### Foodgram - это сайт для обмена рецептами. 

 Возможности для пользователя :point_down:
 

:white_check_mark: Публиковать свои любимые рецепты

:white_check_mark: Просматривать рецепты других пользователей 

:white_check_mark: Добавлять любимые рецепты в избранное

:white_check_mark: Подписываться на других пользователей

:white_check_mark: Составлять свой список покупок с ингредиентами понравившегося рецепта

### Подготовка к запуску :point_down:

:point_right: На сервере создайте папку проекта - foodgram и скопируйте в нее файл docker-compose.production.yml.

:point_right: В папке с проектом создайте файл .env и заполните его своими данными:

**POSTGRES_ON** - True для работы с БД PostgreSQL | False для работы с БД SQLite

**POSTGRES_USER** - имя пользователя для доступа к базе данных

**POSTGRES_PASSWORD** - пароль для доступа к базе данных

**POSTGRES_DB** - имя базы данных

**SECRET_KEY** - секретный ключ для Django

**DEBUG** - True/False - режим отладки Django

**ALLOWED_HOSTS** - список разрешенных хостов

**DB_HOST** - имя хоста базы данных

**DB_PORT** - порт базы данных

### Запуск проекта :point_down:

:point_right: Находясь в папке с проектом скачайте образы и запустите проект командами:

sudo docker compose -f docker-compose.production.yml up -d

:point_right: Выполните миграции, соберите статические файлы бэкенда:

sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

sudo docker compose -f docker-compose.production.yml exec backend mkdir -p backend_static/static/

sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic


:point_right: Создайте суперпользователя:

sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
