from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import add_user_car, get_user_cars, add_user_address, get_user_addresses
from keyboards import get_profile_keyboard, get_back_to_menu_keyboard

# Состояния для ConversationHandler
GETTING_BRAND, GETTING_MODEL, GETTING_YEAR = range(3)
GETTING_ADDRESS = 4

async def show_user_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать автомобили пользователя"""
    user_id = update.effective_user.id
    cars = get_user_cars(user_id)
    
    if not cars:
        keyboard = [['🚗 Добавить автомобиль'], ['↩️ Назад']]
        await update.message.reply_text(
            "У вас пока нет добавленных автомобилей.",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return
    
    cars_text = "🚗 Ваши автомобили:\n\n"
    for car in cars:
        car_id, user_id, brand, model, year = car
        cars_text += f"{brand} {model} ({year} год)\n"
    
    keyboard = [['🚗 Добавить автомобиль'], ['↩️ Назад']]
    await update.message.reply_text(
        cars_text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def add_car_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления автомобиля"""
    await update.message.reply_text(
        "Введите марку автомобиля (например: Geely, Chery, Haval):",
        reply_markup=ReplyKeyboardMarkup([['↩️ Отмена']], resize_keyboard=True)
    )
    return GETTING_BRAND

async def add_car_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение марки автомобиля"""
    context.user_data['car_brand'] = update.message.text
    await update.message.reply_text("Теперь введите модель автомобиля (например: Coolray, Tiggo 7, Jolion):")
    return GETTING_MODEL

async def add_car_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение модели автомобиля"""
    context.user_data['car_model'] = update.message.text
    await update.message.reply_text("Теперь введите год выпуска (например: 2022):")
    return GETTING_YEAR

async def add_car_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение добавления автомобиля"""
    try:
        year = int(update.message.text)
        user_id = update.effective_user.id
        brand = context.user_data.get('car_brand', '')
        model = context.user_data.get('car_model', '')
        
        if not brand or not model:
            await update.message.reply_text(
                "❌ Ошибка: данные автомобиля неполные",
                reply_markup=get_profile_keyboard()
            )
            return ConversationHandler.END
        
        success = add_user_car(user_id, brand, model, year)
        
        if success:
            await update.message.reply_text(
                f"✅ Автомобиль успешно добавлен!\n\n"
                f"Марка: {brand}\n"
                f"Модель: {model}\n"
                f"Год: {year}",
                reply_markup=get_profile_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при добавлении автомобиля",
                reply_markup=get_profile_keyboard()
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите корректный год цифрами (например: 2022)",
            reply_markup=ReplyKeyboardMarkup([['↩️ Отмена']], resize_keyboard=True)
        )
        return GETTING_YEAR
    
    # Очищаем данные
    context.user_data.pop('car_brand', None)
    context.user_data.pop('car_model', None)
    
    return ConversationHandler.END

async def show_user_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать адреса пользователя"""
    user_id = update.effective_user.id
    addresses = get_user_addresses(user_id)
    
    if not addresses:
        keyboard = [['🏠 Добавить адрес'], ['↩️ Назад']]
        await update.message.reply_text(
            "У вас пока нет добавленных адресов.",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return
    
    addresses_text = "🏠 Ваши адреса:\n\n"
    for address in addresses:
        addr_id, user_id, address_text = address
        addresses_text += f"• {address_text}\n"
    
    keyboard = [['🏠 Добавить адрес'], ['↩️ Назад']]
    await update.message.reply_text(
        addresses_text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def add_address_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления адреса"""
    await update.message.reply_text(
        "Введите ваш адрес для доставки (город, улица, дом, квартира):",
        reply_markup=ReplyKeyboardMarkup([['↩️ Отмена']], resize_keyboard=True)
    )
    return GETTING_ADDRESS

async def add_address_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение добавления адреса"""
    address = update.message.text
    user_id = update.effective_user.id
    
    if not address or len(address.strip()) < 5:
        await update.message.reply_text(
            "❌ Адрес слишком короткий. Пожалуйста, введите полный адрес.",
            reply_markup=ReplyKeyboardMarkup([['↩️ Отмена']], resize_keyboard=True)
        )
        return GETTING_ADDRESS
    
    success = add_user_address(user_id, address.strip())
    
    if success:
        await update.message.reply_text(
            f"✅ Адрес успешно добавлен:\n{address}",
            reply_markup=get_profile_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при добавлении адреса",
            reply_markup=get_profile_keyboard()
        )
    
    return ConversationHandler.END

async def show_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать информацию о подписке"""
    await update.message.reply_text(
        "💳 Информация о подписке:\n\n"
        "Подписка дает возможность:\n"
        "• Добавлять товары в корзину\n"
        "• Оформлять заказы\n"
        "• Получать уведомления о скидках\n\n"
        "Стоимость: 499 руб./месяц\n\n"
        "Для оформления подписки свяжитесь с администратором: @support",
        reply_markup=get_profile_keyboard()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена операции"""
    await update.message.reply_text(
        "Операция отменена",
        reply_markup=get_profile_keyboard()
    )
    
    # Очищаем данные
    context.user_data.pop('car_brand', None)
    context.user_data.pop('car_model', None)
    
    return ConversationHandler.END