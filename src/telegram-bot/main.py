import logging
import os
import random
from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

IDEAS_BY_CATEGORY: Dict[str, List[str]] = {
    "Игры": [
        "Настольная игра на 30-40 минут.",
        "Семейная викторина: 10 вопросов про друг друга.",
        "Домашний квест с 5 подсказками по квартире.",
        "Игра в ассоциации: по 3 слова на тему дня.",
        "Мини-турнир в карты/шашки с символическим призом.",
    ],
    "Кино": [
        "Семейный киновечер с выбором фильма голосованием.",
        "Посмотрите короткометражку и обсудите впечатления.",
        "Сделайте тематический вечер: мультфильм + перекус.",
        "Фильм детства одного из родителей + семейные истории.",
        "Кино без телефона: создайте атмосферу как в зале.",
    ],
    "Рецепты": [
        "Приготовьте домашнюю пиццу вместе.",
        "Сделайте семейный десерт без выпечки.",
        "Устройте ужин из блюд одного цвета.",
        "Готовим завтрак на ужин всей семьей.",
        "Новый рецепт недели: каждый делает один шаг.",
    ],
    "Разговоры": [
        "Круг благодарности: каждый говорит 1 хорошую вещь.",
        "Вопрос дня: что сегодня было самым интересным?",
        "План мечты: куда хотите поехать всей семьей?",
        "Вечер воспоминаний по семейным фото.",
        "Игра 'если бы...': по 3 фантазии от каждого.",
    ],
    "Активности": [
        "Вечерняя прогулка новым маршрутом.",
        "Мини-зарядка под любимую музыку.",
        "Семейный пикник во дворе или парке.",
        "Соберите пазл или конструктор вместе.",
        "Фото-охота: 5 объектов, которые нужно найти.",
    ],
}

ALL_CATEGORIES = list(IDEAS_BY_CATEGORY.keys())


def build_categories_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(category, callback_data=f"category:{category}")]
        for category in ALL_CATEGORIES
    ]
    return InlineKeyboardMarkup(buttons)


def random_idea(category: str | None = None) -> str:
    if category and category in IDEAS_BY_CATEGORY:
        return random.choice(IDEAS_BY_CATEGORY[category])

    all_ideas = [
        f"{cat}: {idea}" for cat, ideas in IDEAS_BY_CATEGORY.items() for idea in ideas
    ]
    return random.choice(all_ideas)


def week_plan() -> List[str]:
    days = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    return [f"{day}: {random_idea()}" for day in days]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Привет! Я бот «Идея семейного вечера».\n\n"
        "Помогаю быстро выбрать теплую семейную активность: "
        "игры, кино, рецепты, разговоры и совместные активности.\n\n"
        "Команды:\n"
        "/idea - случайная идея\n"
        "/week - 7 идей на неделю\n"
        "/start - показать это меню"
    )
    await update.message.reply_text(message, reply_markup=build_categories_keyboard())


async def idea_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    idea = random_idea()
    await update.message.reply_text(
        f"Ваша идея на вечер:\n\n{idea}",
        reply_markup=build_categories_keyboard(),
    )


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    plan = week_plan()
    text = "Идеи на 7 дней:\n\n" + "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(plan))
    await update.message.reply_text(text, reply_markup=build_categories_keyboard())


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    payload = query.data or ""
    if not payload.startswith("category:"):
        return

    category = payload.split(":", 1)[1]
    if category not in IDEAS_BY_CATEGORY:
        await query.message.reply_text("Неизвестная категория.")
        return

    idea = random_idea(category)
    await query.message.reply_text(f"{category}:\n\n{idea}")


def validate_token() -> str:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не найден токен. Установите переменную окружения BOT_TOKEN и запустите снова."
        )
    return token


def main() -> None:
    token = validate_token()
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("idea", idea_command))
    application.add_handler(CommandHandler("week", week_command))
    application.add_handler(CallbackQueryHandler(category_callback))

    logger.info("Bot started")
    application.run_polling()


if __name__ == "__main__":
    main()
