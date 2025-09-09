from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать помощь"""
    help_text = """
🤖 <b>Помощь по боту</b>

🔍 <b>Поиск</b> - ищите запчасти по артикулу или названию
🧺 <b>Корзина</b> - добавляйте товары и оформляйте заказы
👤 <b>Личный кабинет</b> - управляйте подпиской и своими данными
❤️ <b>Избранное</b> - сохраняйте понравившиеся товары

💳 <b>Подписка</b> дает возможность:
• Добавлять товары в корзину
• Оформлять заказы
• Получать уведомления о скидках

📞 Для связи: @support
    """
    await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=get_main_menu_keyboard())