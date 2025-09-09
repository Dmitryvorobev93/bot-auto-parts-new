from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from decorators import check_subscription

@check_subscription
async def checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Оформление заказа (только для подписанных пользователей)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    # Логика оформления заказа
    # ...
    
    await query.edit_message_text("✅ Заказ оформлен! Менеджер свяжется с вами для подтверждения.")