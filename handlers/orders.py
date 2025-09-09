from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from decorators import check_subscription

@check_subscription
async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оформление заказа"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("✅ Заказ оформлен! Менеджер свяжется с вами для подтверждения.")