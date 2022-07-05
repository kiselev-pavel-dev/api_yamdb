# YaMDb API (v1)


## Описание:

Проект YaMDb собирает отзывы пользователей на произведения различных категорий и жанров.

> API предоставляет другим программам базовый функционал для взаимодействия с проектом. 

## Стек:

Python, Django Rest Framework, SQLite

## Установка (Windows):

1. Клонировать репозиторий и перейти в него в командной строке:

    ```
    git clone git@github.com:kiselev-pavel-dev/api_yamdb.git
    ```

    ```
    cd api_yamdb
    ```

2. Cоздать и активировать виртуальное окружение:

    ```
    python -m venv venv
    ```

    ```
    source venv/scripts/activate
    ```

3. Установить зависимости из файла requirements.txt:

    ```
    python -m pip install --upgrade pip
    ```

    ```
    pip install -r requirements.txt
    ```

4. Выполнить миграции:

    ```
    python manage.py migrate
    ```

5. Запустить проект:

    ```
    python manage.py runserver
    ```

## Примеры запросов:

Регистрация нового пользователя:

```
POST /api/v1/auth/signup/
```

Получение JWT-токена:

```
POST /api/v1/auth/token/
```

Получение списка всех пользователей:

```
GET /api/v1/users/
```

Добавление пользователя по username:

```
POST /api/v1/users/{username}/
```

Удаление категории:

```
DELETE /api/v1/categories/{slug}/
```

Получение списка всех жанров:

```
GET /api/v1/genres/
```

Получение информации о произведении:

```
GET /api/v1/titles/{titles_id}/
```

Частичное обновление отзыва по id:

```
PATCH /api/v1/titles/{title_id}/reviews/{review_id}/
```

Удаление комментария к отзыву:

```
DELETE /api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
