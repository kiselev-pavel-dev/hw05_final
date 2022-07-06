# Yatube

## Описание:

Данный проект представляет собой социальную сеть, в которой пользователи могут регистрироваться, публиковать посты, подписываться на других авторов, оставлять комментарии к постам.

## Стек:

Python, Django, SQLite, Pytest, HTML

## Как запустить проект (Windows):

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/pavel-kiselev-practicum/hw05_final
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать миграции:

```
python3 manage.py makemigrations
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
