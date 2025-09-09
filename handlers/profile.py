from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_profile_keyboard, get_back_to_menu_keyboard

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Здесь логика проверки подписки пользователя из БД
    # user_data = get_user(user_id)
    # is_subscribed = user_data['subscribed']

    profile_text = f"""
👤 Ваш личный кабинет

Статус подписки: {'✅ Активна' if False else '❌ Не активна'}
    """
    await update.message.reply_text(profile_text, reply_markup=get_profile_keyboard())

async def add_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Логика для FSM: запрос марки -> модели -> года -> сохранение в БД
    await update.message.reply_text("Введите марку вашего автомобиля:", reply_markup=get_back_to_menu_keyboard())
    # return STATE_CAR_BRAND