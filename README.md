# Telegram Bot для Парсинга Сайтов с Зюзюбликами
Этот проект представляет собой Telegram бота на Python, который позволяет пользователям загружать Excel-файлы с информацией о сайтах для парсинга цен на зюзюблики. Бот обрабатывает файлы, сохраняет данные в PostgreSQL и выполняет парсинг цен с указанных сайтов.
## Установка и запуск
1. Клонируйте репозиторий:
```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```
2. Создайте файл .env в корневом каталоге проекта со следующими переменными:
```bash
BOT_TOKEN = your_telegram_bot_token
DB_HOST = localhost
DB_PORT = 5432
DB_USER = your_username
DB_PASS = your_password
DB_NAME = doc_process
```
3. Установите зависимости:
```bash
pip install -r requirements.txt
```
4. Запустите Docker-контейнер:
```bash
docker-compose up -d
```
## Использование
1. Найдите своего бота в Telegram по его имени.
2. Отправьте команду /start для начала работы с ботом.
3. Нажмите на кнопку "Загрузить файл" и загрузите Excel-файл с колонками:
    - title - название сайта
    - url - ссылка на сайт
    - xpath - XPath-путь к элементу с ценой на странице
5. Для тестирования функционала можете взять файл **data.xlsx**, который находится в **example_data** 

4. Бот обработает файл, покажет его содержимое и сохранит данные в базу.
5. Бот также выполнит парсинг цен с указанных сайтов и покажет среднюю цену по каждому сайту.
## Формат файла Excel
Пример правильного формата Excel-файла:

| title | url |           xpath            |
|:--------------:|:---------:|:--------------------------:|
| Магазин зюзюбликов | https://example1.com | //div[@class='price']/span |
| Мир зюзюбликов | https://example2.com |  //span[@id='item-price']  |