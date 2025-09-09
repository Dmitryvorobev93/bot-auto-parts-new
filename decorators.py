from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from database import get_user

def check_subscription(func):
    """Декоратор для проверки подписки пользователя"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Получаем данные пользователя из БД
        user_data = get_user(user_id)
        if not user_data:
            await update.message.reply_text("❌ Пользователь не найден. Начните с /start")
            return
        
        # Проверяем статус подписки (user_data - это кортеж, подписка в индексе 4)
        is_subscribed = user_data[4] if len(user_data) > 4 else False
        
        if not is_subscribed:
            # Проверяем тип update и отправляем сообщение соответственно
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text(
                    "❌ Для этого действия нужна подписка!\n"
                    "Оформите подписку в 👤 Личном кабинете"
                )
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.answer(
                    "❌ Нужна подписка! Откройте Личный кабинет",
                    show_alert=True
                )
            return
        
        # Если подписка есть, выполняем оригинальную функцию
        return await func(update, context, *args, **kwargs)
    return wrapped