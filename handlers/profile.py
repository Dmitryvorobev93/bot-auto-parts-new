from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_profile_keyboard, get_main_menu_keyboard

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Личный кабинет"""
    user = update.effective_user
    
    profile_text = f"""
👤 <b>Ваш личный кабинет</b>

🆔 ID: {user.id}
👤 Имя: {user.first_name}
📱 Username: @{user.username or 'не указан'}

💳 <b>Статус подписки:</b> ❌ Не активна

Выберите действие:
• 🚗 Мои автомобили - управление вашими автомобилями
• 🏠 Мой адрес - управление адресами доставки
• 💳 Купить подписку - доступ к оформлению заказов
    """
    
    await update.message.reply_text(profile_text, parse_mode='HTML', reply_markup=get_profile_keyboard())