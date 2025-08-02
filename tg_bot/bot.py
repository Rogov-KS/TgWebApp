#!/usr/bin/env python3
"""
Telegram бот для тестирования интеграции с Web App.

Использует aiogram для создания бота с кнопкой для запуска Web App.
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
    exit(1)

# URL вашего Web App (замените на реальный URL)
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "https://your-domain.com")

# Создаем экземпляры бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """
    Обработчик команды /start.

    Отправляет приветственное сообщение с кнопкой для запуска Web App.
    """
    user = message.from_user

    # Создаем приветственное сообщение
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "🎮 Добро пожаловать в игру Snake!\n\n"
        "🎯 Нажмите кнопку ниже, чтобы начать игру в Web App.\n\n"
        "📱 Игра будет открыта прямо в Telegram."
    )

    # Создаем кнопку для запуска Web App
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Начать игру", web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [InlineKeyboardButton(text="ℹ️ Информация", callback_data="info")],
        ]
    )

    await message.answer(welcome_text, reply_markup=keyboard)


@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """
    Обработчик команды /help.

    Отправляет справку по использованию бота.
    """
    help_text = (
        "🤖 **Справка по боту Snake Game**\n\n"
        "📋 **Доступные команды:**\n"
        "• `/start` - Запустить игру\n"
        "• `/help` - Показать эту справку\n"
        "• `/info` - Информация об игре\n"
        "• `/stats` - Ваша статистика\n\n"
        "🎮 **Как играть:**\n"
        "1. Нажмите кнопку '🎮 Начать игру'\n"
        "2. Игра откроется в Web App\n"
        "3. Управляйте змейкой стрелками\n"
        "4. Собирайте еду для роста\n"
        "5. Избегайте столкновений\n\n"
        "🏆 **Цель:** Набрать как можно больше очков!"
    )

    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("info"))
async def cmd_info(message: types.Message) -> None:
    """
    Обработчик команды /info.

    Отправляет информацию об игре.
    """
    info_text = (
        "🎮 **Snake Game - Информация**\n\n"
        "📱 **Web App технология:**\n"
        "• Игра работает прямо в Telegram\n"
        "• Не требует установки\n"
        "• Автоматическая авторизация\n\n"
        "🎯 **Особенности:**\n"
        "• Классическая игра Snake\n"
        "• Сохранение рекордов\n"
        "• Таблица лидеров\n"
        "• Различные уровни сложности\n\n"
        "🔐 **Безопасность:**\n"
        "• Проверенная авторизация через Telegram\n"
        "• Защищенные данные пользователя\n"
        "• Безопасное хранение результатов\n\n"
        "💡 **Советы:**\n"
        "• Начните с медленной скорости\n"
        "• Планируйте маршрут заранее\n"
        "• Не торопитесь на высоких уровнях"
    )

    await message.answer(info_text, parse_mode="Markdown")


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message) -> None:
    """
    Обработчик команды /stats.

    Показывает статистику пользователя (заглушка).
    """
    user = message.from_user

    # Здесь можно добавить запрос к API для получения реальной статистики
    stats_text = (
        f"📊 **Статистика игрока {user.first_name}**\n\n"
        "🎮 **Игры сыграно:** 0\n"
        "🏆 **Лучший результат:** 0 очков\n"
        "📈 **Средний результат:** 0 очков\n"
        "🥇 **Место в рейтинге:** Не определено\n\n"
        "💡 *Для получения актуальной статистики запустите игру!*"
    )

    await message.answer(stats_text, parse_mode="Markdown")


@dp.callback_query(lambda c: c.data == "info")
async def process_info_callback(callback_query: types.CallbackQuery) -> None:
    """
    Обработчик callback для кнопки "Информация".
    """
    info_text = (
        "ℹ️ **О боте Snake Game**\n\n"
        "🎮 Это классическая игра Snake, адаптированная для Telegram Web App.\n\n"
        "🔧 **Технологии:**\n"
        "• Backend: FastAPI + PostgreSQL\n"
        "• Frontend: React + TypeScript\n"
        "• Telegram: Web App API\n\n"
        "🚀 **Возможности:**\n"
        "• Автоматическая авторизация\n"
        "• Сохранение результатов\n"
        "• Таблица лидеров\n"
        "• Адаптивный дизайн\n\n"
        "📞 **Поддержка:**\n"
        "По вопросам обращайтесь к разработчику."
    )

    await callback_query.message.answer(info_text, parse_mode="Markdown")
    await callback_query.answer()


@dp.message()
async def echo_message(message: types.Message) -> None:
    """
    Обработчик всех остальных сообщений.

    Отправляет подсказку о доступных командах.
    """
    help_text = (
        "🤖 Не понимаю эту команду.\n\n"
        "📋 **Доступные команды:**\n"
        "• `/start` - Запустить игру\n"
        "• `/help` - Справка\n"
        "• `/info` - Информация\n"
        "• `/stats` - Статистика\n\n"
        "🎮 Нажмите /start для начала игры!"
    )

    await message.answer(help_text)


async def main() -> None:
    """
    Главная функция для запуска бота.
    """
    logger.info("🚀 Запуск Telegram бота...")

    # Проверяем доступность бота
    try:
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот успешно подключен: @{bot_info.username}")
        logger.info(f"📱 Имя бота: {bot_info.first_name}")
        logger.info(f"🔗 Web App URL: {WEBAPP_URL}")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к боту: {e}")
        return

    # Запускаем бота
    try:
        logger.info("🔄 Запуск диспетчера...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Остановка бота...")
    except Exception as e:
        logger.error(f"❌ Ошибка в работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
