from telegram import Update
from telegram.ext import ContextTypes

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка предварительного запроса платежа"""
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка успешного платежа"""
    await update.message.reply_text("✅ Спасибо за оплату! Ваша подписка активирована.")