# Проект "Фудграм" - сайт для публикации своих рецептов.

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Описание

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Как запустить проект на удаленном сервере:

1. Клонировать репозиторий на локальный компьютер и перейти в него в командной строке:

```
git clone https//:github.com/Dmitri-prog/foodgram-project-react.git
```

```
cd foodgram-project-react
```

2. Cоздать в корне проекта файл .env и заполнить его (пример файла .env см. в приложенном файле .env.example). Описание переменных виртуального окружения файла .env для работы проекта:
```
POSTGRES_USER - имя пользователя БД;
POSTGRES_PASSWORD - пароль пользователя БД;
POSTGRES_DB - название БД PostgreSQL;
DB_HOST - адрес, по которому Django будет соединяться с базой данных. При работе нескольких контейнеров в сети Docker network вместо адреса указывают имя контейнера, где запущен сервер БД;
DB_PORT - порт, по которому Django будет обращаться к базе данных. Порт по умолчанию для PostgreSQL - 5432;
SECRET_KEY - cекретный ключ установки Django. Он используется в контексте криптографической подписи и должен иметь уникальное, непредсказуемое значение. Новый оригинальный секретный ключ можно получить при помощи функции get_random_secret_key(), импортируемой из django.core.management.utils;
DEBUG - настройка вывода отладочной информации в Django-проекте, указывается в файле settings.py, при развертывании проекта должно быть установлено значение False
ALLOWED_HOSTS - список хостов/доменов, для которых может работать текущий проект. По умолчанию доступны хосты '127.0.0.1' и 'localhost'.
```

3. Создать Docker-образы проекта. Замените username на Ваш логин на DockerHub:

```
cd frontend
```

```
docker build -t username/foodgram_frontend .
```

```
cd ../backend/foodgram
```

```
docker build -t username/foodgram_backend .
```

```
cd ../../gateway
```

```
docker build -t username/foodgram_gateway .
```

4. Загрузить созданные образы на DockerHub. Замените username на Ваш логин на DockerHub:
```
docker push username/foodgram_frontend
```

```
docker push username/foodgram_backend
```

```
docker push username/foodgram_gateway
```

5. Подключиться к удаленному серверу:
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
```

6. Создать на сервере через терминал директорию foodgram:
```
mkdir foodgram
```

7. Установить docker compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

8. На локальном компьютере из дирректории foodgram-project-react/ cкопировать на сервер в директорию foodgram/ файл docker-compose.production.yml и .env:
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```

```
scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env
```

Где:
```
path_to_SSH — путь к файлу с SSH-ключом;
SSH_name — имя файла с SSH-ключом (без расширения);
username — Ваше имя пользователя на сервере;
server_ip — IP вашего сервера.
```

9. Запустить на сервере docker compose в режиме демона:
```
sudo docker compose -f docker-compose.production.yml up -d
```
10. На сервере выполнить миграции, собрать статические файлы бэкенда и скопировать их в /backend_static/static/, а также загрузить список ингредиентов:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients_into_db
```
11. На сервере в редакторе Nano открыть файл настроек Nginx:
```
sudo nano /etc/nginx/sites-enabled/default
```
12. В файле настроек Nginx через редактор Nano указать для проекта настройки location в секции server:
```
location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
```
13. Чтобы убедиться, что в конфиге (файле настроек) Nginx нет ошибок — выполнить команду проверки конфигурации:
```
sudo nginx -t
```
14. Перезагрузить конфиг Nginx:
```
sudo service nginx reload
```
14. Перейти на страницу проекта по адресу https://ваш_домен_проекта/ и убедиться в его работоспособности.

## Как настроить CI/CD проекта и уведомления о деплое от Telegram-бота:

1. В дирректории .github/workflows приложен готовый файл main.yml для организации CI/CD проекта через GitAction и уведомлений через телеграм-бота.
2. Для выполнения CI/CD проекта, необходимо в Вашем аккаунте на GitHub для данного проекта создать секреты. 
Перейти в настройки репозитория проекта — Settings, выбрать на панели слева Secrets and Variables → Actions, нажать New repository secret. Необходимо создать следующие секреты:
```
DOCKER_USERNAME - имя пользователя в DockerHub;
DOCKER_PASSWORD - пароль пользователя в DockerHub;
HOST - IP удаленного сервера;
USER - имя Вашего пользователя на удаленном сервере;
SSH_KEY - содержимое текстового файла с закрытым SSH-ключом для доступа к удаленному серверу;
SSH_PASSPHRASE - passphrase для закрытого SSH-ключа.
```
3. Для получения уведомлений от телеграм-бота об успешном деплое проекта необходимо в Вашем аккаунте на GitHub для GitAction создать следующие секреты:
```
TELEGRAM_TO - ID Вашего телеграм-аккаунта, можно узнать у телеграм-бота @userinfobot;
TELEGRAM_TOKEN - токен Вашего телеграм-бота, получить этот токен можно у телеграм-бота @BotFather.
```
## Примеры некоторых запросов API

Регистрация пользователя:

```bash
   POST /api/v1/users/
```

Получение данных своей учетной записи:

```bash
   GET /api/v1/users/me/ 
```

Добавление подписки:

```bash
   POST /api/v1/users/id/subscribe/
```

Обновление рецепта:
  
```bash
   PATCH /api/v1/recipes/id/
```

Удаление рецепта из избранного:

```bash
   DELETE /api/v1/recipes/id/favorite/
```

Получение списка ингредиентов:

```bash
   GET /api/v1/ingredients/
```

Скачать список покупок:

```bash
   GET /api/v1/recipes/download_shopping_cart/
```

Проект доступен по адресу: <http://foodgramm.ddns.net/>

Доступ в админ-зону сайта:

```bash
   email - user_main@mail.ru
   пароль - I_am_main
```


## Полный список запросов API находятся в документации

```
   foodgram-project-react/docs/redoc.html
```

#### Автор

Марков Дмитрий - [https://github.com/Dmitri-prog/](https://github.com/Dmitri-prog/)
