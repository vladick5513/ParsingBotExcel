import os
import logging
import pandas as pd
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import aiohttp
from lxml import html
import re

from app.database import async_session_factory
from app.bot.crud import create_sources_bulk, update_sources_prices_bulk, get_all_sources

router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Функция для нормализации цен
def normalize_price(price_text):
    if not price_text:
        return None

    # Удаление всех нецифровых символов, кроме точки и запятой
    price_text = re.sub(r'[^\d.,]', '', price_text)

    # Замена запятой на точку
    price_text = price_text.replace(',', '.')

    try:
        return float(price_text)
    except ValueError:
        return None


# Функция для парсинга цены с сайта
async def parse_price(url, xpath):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    tree = html.fromstring(content)
                    elements = tree.xpath(xpath)

                    if elements:
                        price_text = elements[0].text_content().strip()
                        return normalize_price(price_text)
    except Exception as e:
        logging.error(f"Error parsing {url}: {e}")

    return None


# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = ReplyKeyboardBuilder()
    kb.button(text="Загрузить файл")
    await message.answer(
        "Привет! Я помогу вам добавить сайты для парсинга зюзюбликов. "
        "Нажмите на кнопку, чтобы загрузить Excel-файл.",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


# Обработчик нажатия на кнопку "Загрузить файл"
@router.message(F.text == "Загрузить файл")
async def upload_file_request(message: types.Message):
    await message.answer(
        "Пожалуйста, загрузите Excel-файл в формате таблицы с полями:\n"
        "- title (название)\n"
        "- url (ссылка на сайт источник)\n"
        "- xpath (путь к элементу с ценой)"
    )


# Обработчик загрузки файла
@router.message(F.document)
async def process_file(message: types.Message):
    # Проверка расширения файла
    if not message.document.file_name.endswith(('.xlsx', '.xls')):
        await message.answer("Пожалуйста, загрузите файл Excel (.xlsx или .xls)")
        return

    # Скачивание файла
    await message.answer("Получен файл. Обрабатываю...")
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file_path = file_info.file_path

    # Создаем временный путь для сохранения файла
    temp_file = f"temp_{message.from_user.id}.xlsx"
    await message.bot.download_file(file_path, temp_file)

    try:
        # Чтение данных из Excel
        df = pd.read_excel(temp_file)

        # Проверка наличия необходимых колонок
        required_columns = ['title', 'url', 'xpath']
        if not all(col in df.columns for col in required_columns):
            await message.answer(
                "Ошибка: В файле отсутствуют обязательные колонки (title, url, xpath)."
            )
            os.remove(temp_file)
            return

        # Форматируем содержимое для лучшего отображения в Telegram
        rows_count = min(len(df), 10)  # Ограничиваем количество строк для превью
        preview = "📋 Содержимое файла:\n\n"

        for i in range(rows_count):
            row = df.iloc[i]
            preview += f"*Запись #{i + 1}:*\n"
            preview += f"📝 *Название:* {row['title']}\n"
            preview += f"🔗 *URL:* {row['url']}\n"
            preview += f"🔍 *XPath:* {row['xpath']}\n\n"

        if len(df) > rows_count:
            preview += f"...и еще {len(df) - rows_count} записей"

        # Отправляем предварительный просмотр
        await message.answer(preview, parse_mode="Markdown")

        # Преобразуем DataFrame в список словарей
        sources_data = df.to_dict('records')

        # Сохранение в базу данных
        async with async_session_factory() as session:
            try:
                # Сохраняем все источники
                sources = await create_sources_bulk(session, sources_data)
                await message.answer(f"✅ Данные успешно сохранены в базу данных. Добавлено {len(sources)} источников.")

                # Задача со звездочкой: парсинг и расчет средней цены
                await message.answer("⏳ Начинаю парсинг цен с указанных сайтов...")

                # Создаем список задач для асинхронного парсинга
                tasks = []
                for source in sources:
                    task = parse_price(source.url, source.xpath)
                    tasks.append((source.id, task))

                # Выполняем все задачи параллельно
                price_results = {}
                for source_id, task in tasks:
                    price = await task
                    if price is not None:
                        price_results[source_id] = price

                if price_results:
                    # Обновляем средние цены в базе данных
                    await update_sources_prices_bulk(session, price_results)

                    # Получаем обновленные данные для отчета
                    all_sources = await get_all_sources(session)

                    # Формируем отчет о средних ценах
                    price_report = "💰 *Средние цены зюзюбликов по сайтам:*\n\n"
                    for source in all_sources:
                        if source.avg_price is not None:
                            price_report += f"*{source.title}*: {source.avg_price:.2f} ₽\n"
                        else:
                            price_report += f"*{source.title}*: ❌ Не удалось получить цену\n"

                    await message.answer(price_report, parse_mode="Markdown")
                else:
                    await message.answer("❌ Не удалось получить цены ни с одного сайта.")

            except Exception as e:
                await session.rollback()
                await message.answer(f"❌ Ошибка при сохранении данных: {e}")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла: {e}")
    finally:
        # Удаление временного файла
        os.remove(temp_file)