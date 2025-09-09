from telegram import Update, LabeledPrice
from telegram.ext import ContextTypes, PreCheckoutQueryHandler
from config import PROVIDER_TOKEN

async def create_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    title = "Премиум подписка на 1 месяц"
    description = "Доступ к оформлению заказов и доставке запчастей."
    payload = f"subscription_{chat_id}" # Уникальный идентификатор
    currency = "RUB"
    price = 499 # Цена
    prices = [LabeledPrice("Подписка", price * 100)] # Цена в мелких единицах (копейки)

    await context.bot.send_invoice(
        chat_id, title, description, payload,
        PROVIDER_TOKEN, currency, prices,
        need_name=False, need_phone=False, need_email=False,
        need_shipping_address=False, is_flexible=False
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    # Проверить данные, если нужно
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обработать успешный платеж
    user_id = update.effective_user.id
    payment_info = update.message.successful_payment
    # Обновить БД: UPDATE users SET subscribed=1, subscription_end=<дата> WHERE user_id=?
    await update.message.reply_text("✅ Спасибо за оплату! Ваша подписка активирована.")