from telegram import Update
from telegram.ext import ContextTypes
from database import add_user
from keyboards import get_main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name, user.last_name)

    welcome_text = f"""
Привет, {user.first_name}! 👋
Добро пожаловать в бот по продаже автозапчастей для китайских автомобилей.

Здесь вы можете найти необходимые запчасти по артикулу или названию.

🔍 **Поиск** - найти нужную деталь
🧺 **Корзина** - ваши отобранные товары
👤 **Личный кабинет** - управление подпиской и данными
    """
    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())