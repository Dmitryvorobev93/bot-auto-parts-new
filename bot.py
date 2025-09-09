import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db

# Импорты обработчиков
from handlers.start import start
from handlers.profile import profile
from handlers.search import search_start, handle_search, add_to_cart_callback
from handlers.cart import show_cart, cart_button_handler
from handlers.orders import checkout_handler
from handlers.payment import precheckout_callback, successful_payment_callback
from handlers.help import show_help
from handlers.favorites import show_favorites
from handlers.car_handler import show_user_cars, start_adding_car, handle_car_brand, handle_car_model, handle_car_year, cancel_adding_car
from handlers.address_handler import show_user_addresses, start_adding_address, handle_address_input, cancel_adding_address
from handlers.profile_handlers import show_subscription

# Импорты админ-панели
from admin import admin_panel, is_admin
from admin import admin_add_part_start, admin_get_article, admin_get_name, admin_get_description, admin_get_price, admin_get_category
from admin import admin_edit_part_start, admin_show_stats, admin_cancel, admin_back
from admin import GET_ARTICLE, GET_NAME, GET_DESCRIPTION, GET_PRICE, GET_CATEGORY

from keyboards import get_main_menu_keyboard

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /admin для администраторов"""
    if is_admin(update.effective_user.id):
        await admin_panel(update, context)
    else:
        await update.message.reply_text("❌ У вас нет прав доступа к этой команде")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Умный обработчик текстовых сообщений"""
    text = update.message.text
    
    # Обработка кнопки "Назад в меню" - возврат в ГЛАВНОЕ меню
    if text == '↩️ Назад в меню':
        # Сбрасываем все режимы
        context.user_data.pop('search_mode', None)
        context.user_data.pop('adding_car', None)
        context.user_data.pop('adding_address', None)
        await start(update, context)
        return
    
    # Обработка кнопки "Назад" - возврат в личный кабинет
    if text == '↩️ Назад':
        # Сбрасываем все режимы
        context.user_data.pop('search_mode', None)
        context.user_data.pop('adding_car', None)
        context.user_data.pop('adding_address', None)
        await profile(update, context)
        return
    
    # Обработка кнопки "Отмена"
    if text == '↩️ Отмена':
        if context.user_data.get('adding_car'):
            await cancel_adding_car(update, context)
            return
        elif context.user_data.get('adding_address'):
            await cancel_adding_address(update, context)
            return
    
    # Проверяем, в каком процессе находится пользователь
    if context.user_data.get('adding_car'):
        car_step = context.user_data.get('car_step')
        if car_step == 'brand':
            await handle_car_brand(update, context)
        elif car_step == 'model':
            await handle_car_model(update, context)
        elif car_step == 'year':
            await handle_car_year(update, context)
        return
    
    elif context.user_data.get('adding_address'):
        await handle_address_input(update, context)
        return
    
    # Проверяем режим поиска - если активен, обрабатываем как поисковый запрос
    elif context.user_data.get('search_mode'):
        await handle_search(update, context)
        return
    
    # Если пользователь вводит текст без активного режима, предлагаем начать поиск
    else:
        # Автоматически активируем режим поиска для любого текстового сообщения
        # если нет других активных режимов
        context.user_data['search_mode'] = True
        await handle_search(update, context)

def main() -> None:
    # Инициализируем базу данных
    init_db()

    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для добавления автомобиля
    car_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🚗 Добавить автомобиль$'), start_adding_car)],
        states={
            'brand': [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_car_brand)],
            'model': [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_car_model)],
            'year': [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_car_year)],
        },
        fallbacks=[MessageHandler(filters.Regex('^↩️ Отмена$'), cancel_adding_car)]
    )
    
    # ConversationHandler для добавления адреса
    address_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🏠 Добавить адрес$'), start_adding_address)],
        states={
            'address': [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address_input)],
        },
        fallbacks=[MessageHandler(filters.Regex('^↩️ Отмена$'), cancel_adding_address)]
    )

    # ConversationHandler для админ-панели (добавление товаров)
    admin_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_add_part_start, pattern="^admin_add_part$")],
        states={
            GET_ARTICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_article)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_name)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_description)],
            GET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_price)],
            GET_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_get_category)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel)]
    )

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Обработчики ConversationHandler
    application.add_handler(car_conv_handler)
    application.add_handler(address_conv_handler)
    application.add_handler(admin_conv_handler)
    
    # Обработчики кнопок главного меню
    application.add_handler(MessageHandler(filters.Regex('^🔍 Поиск запчастей$'), search_start))
    application.add_handler(MessageHandler(filters.Regex('^🧺 Корзина$'), show_cart))
    application.add_handler(MessageHandler(filters.Regex('^❤️ Избранное$'), show_favorites))
    application.add_handler(MessageHandler(filters.Regex('^👤 Личный кабинет$'), profile))
    application.add_handler(MessageHandler(filters.Regex('^🆘 Помощь$'), show_help))
    application.add_handler(MessageHandler(filters.Regex('^↩️ Назад в меню$'), start))
    
    # Обработчики кнопок личного кабинета
    application.add_handler(MessageHandler(filters.Regex('^🚗 Мои автомобили$'), show_user_cars))
    application.add_handler(MessageHandler(filters.Regex('^🏠 Мой адрес$'), show_user_addresses))
    application.add_handler(MessageHandler(filters.Regex('^💳 Купить подписку$'), show_subscription))
    application.add_handler(MessageHandler(filters.Regex('^↩️ Назад$'), profile))
    
    # Обработчики добавления данных
    application.add_handler(MessageHandler(filters.Regex('^🚗 Добавить автомобиль$'), start_adding_car))
    application.add_handler(MessageHandler(filters.Regex('^🏠 Добавить адрес$'), start_adding_address))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(cart_button_handler, pattern="^cart_"))
    application.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern="^add_"))
    application.add_handler(CallbackQueryHandler(add_to_cart_callback, pattern="^new_search$"))
    application.add_handler(CallbackQueryHandler(checkout_handler, pattern="^checkout$"))
    
    # Обработчики callback для админ-панели
    application.add_handler(CallbackQueryHandler(admin_edit_part_start, pattern="^admin_edit_part$"))
    application.add_handler(CallbackQueryHandler(admin_show_stats, pattern="^admin_stats$"))
    application.add_handler(CallbackQueryHandler(admin_back, pattern="^admin_back$"))

    # Запускаем бота
    print("Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()