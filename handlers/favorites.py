from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu_keyboard

async def show_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать избранное (временная заглушка)"""
    await update.message.reply_text(
        "❤️ Раздел 'Избранное' в разработке. Скоро будет доступен!",
        reply_markup=get_main_menu_keyboard()
    )