# TZ

### Требования
- Всё настроено для запуска в докер контейнерах (`docker`, `docker-compose`)  
- В PostgreSQL необходимо подключить модуль `intarray`:
```postgresql
CREATE EXTENSION IF NOT EXISTS intarray;
```

### Запуск через докер
```bash
docker-compose up -d
```
- При необходимости запустить бд также в контейнере, следует раскомментировать в `docker-compose.yml` сервис `db` (и `links` для `app` соответсвенно).  
- При необходимости готовых тестовых таблиц - воостановить дамп:
```bash
docker exec -ti <container_id> pg_restore -d db /dump/dump.tar -c -U user
```
юзеров - 10000  
фильмов - 50  
- При использовании ваших таблиц - изменить переменные окружения (ниже).  

### Запуск локально (dev server)
Обязательна правка/добавление переменных окружения (ниже), либо изменить дефолтные значения в основных переменных в коде.  
Из директории с файлом `server.py`
```bash
pip install -r requirements.txt
python3 server.py
```

### Переменныe окружения
- При запуске докер-композом, переменные достаточно добавить в файл .env
- При запуске без докера прописать самостоятельно

#### Список переменных
| ENV_name | DEFAUL VALUE | DESCRIPTION |
|---|---|---|
| DB_HOST | 127.0.0.1 | Хост БД PostgreSQL |
| DB_PORT | 5432 | Порт БД PostgreSQL |
| DB_USER | user | Имя юзера БД PostgreSQL |
| DB_PASSWORD | password | Пароль юзера БД PostgreSQL |
| DB_NAME | db | Имя БД PostgreSQL |
|   |   |   |
| TN_MOVIE | movie | Имя таблицы со списком фильмов |
| TN_PROFILE_MOVIE | profile_movie | Имя таблицы с relations (id пользователья - id просмотренного фильма) |
| CN_MOVIE_ID | movie_id | Имя поля с id фильма (в таблицах TN_MOVIE и TN_PROFILE_MOVIE) |
| CN_PROFILE_ID | profile_id | Имя поля с id пользователя в TN_PROFILE_MOVIE |
| CN_TITLE | title | Имя поля с названием фильма в TN_MOVIE |

*CN - column name  
*TN - table name  

#### Endpoints

- GET / 
    - index 
- GET `/movies_rec/{profile_id}`
    - получение рекомендаций фильмов для профиля с id `profile_id`
    - response
        - Content-Type →application/json; charset=utf-8
        - Порядок списка - от наиболее рекомендованного к наименее
        - Пример
```json
[
    {
        "movie_id": 3,
        "title": "Grumpier Old Men (1995)",
        "views": 5019
    },
    {
        "movie_id": 21,
        "title": "Copycat (1995)",
        "views": 5001
    },
    {
        "movie_id": 14,
        "title": "Cutthroat Island (1995)",
        "views": 4989
    }
]
```
*views - общее количество просмотров фильма другими пользователями с похжим\* списком просмотренных  
**Похожий список фильмов - от 2 одинаковых просмотренных фильмов (записано в константу `MIN_INTERSECT`)  

Среднее время HTTP запроса получил 150 - 250 ms (10000 пользователей, 50 фильмов)  

#### PS
Юниты не писал, т.к. из функций только одна и та - обычный SQL запрос.  
Можно было бы и его потестить, но пока руки не дошли до создания нормальной (не рандомной как в дампе) выборки данных в таблицах.  

##### PPS
Как я запускал и проверял (с раскомментированным сервисом db в .yml):
```bash
    docker-compose up -d
    sleep 5 # запуск postgresql
    docker exec -ti <container_id> pg_restore -d db /dump/dump.tar -c -U user
    # password: password
    curl http://localhost:5858
    curl http://localhost:5858/movies_rec/1234
    curl http://localhost:5858/movies_rec/1
    curl http://localhost:5858/movies_rec/13
    curl http://localhost:5858/movies_rec/5000
```