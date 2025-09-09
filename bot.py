import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config import BOT_TOKEN
from database import init_db
from handlers import start, profile, search, cart, orders, payment
from handlers.cart import cart_button_handler, show_cart
from handlers.orders import checkout_handler
from handlers.payment import precheckout_callback, successful_payment_callback
from telegram.ext import PreCheckoutQueryHandler, MessageHandler, filters

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    # Инициализируем базу данных
    init_db()

    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start.start))
    application.add_handler(MessageHandler(filters.Regex('^🔍 Поиск запчастей$'), search.search_start))
    application.add_handler(MessageHandler(filters.Regex('^👤 Личный кабинет$'), profile.profile))
    application.add_handler(MessageHandler(filters.Regex('^🧺 Корзина$'), cart.show_cart))
    application.add_handler(MessageHandler(filters.Regex('^↩️ Назад в меню$'), start.start))

    # Добавляем обработчики корзины
    application.add_handler(MessageHandler(filters.Regex('^🧺 Корзина$'), show_cart))
    application.add_handler(CallbackQueryHandler(cart_button_handler, pattern="^cart_"))
    application.add_handler(CallbackQueryHandler(checkout_handler, pattern="^checkout$"))
    
    # Добавляем обработчики платежей
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Обработчики callback-запросов (нажатия на inline-кнопки)
    application.add_handler(CallbackQueryHandler(cart.cart_button_handler, pattern="^cart_"))
    application.add_handler(CallbackQueryHandler(orders.checkout_handler, pattern="^checkout$"))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()