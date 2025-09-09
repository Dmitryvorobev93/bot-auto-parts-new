from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        ['🔍 Поиск запчастей'],
        ['🧺 Корзина', '❤️ Избранное'],
        ['👤 Личный кабинет', '🆘 Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_profile_keyboard():
    """Меню личного кабинета"""
    keyboard = [
        ['🚗 Мои автомобили', '🏠 Мой адрес'],
        ['💳 Купить подписку'],
        ['↩️ Назад в меню']  # Возврат в ГЛАВНОЕ меню
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_menu_keyboard():
    """Кнопка возврата в главное меню"""
    keyboard = [['↩️ Назад в меню']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_profile_keyboard():
    """Кнопка возврата в личный кабинет"""
    keyboard = [['↩️ Назад']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cars_keyboard():
    """Меню управления автомобилями"""
    keyboard = [
        ['🚗 Добавить автомобиль'],
        ['↩️ Назад в меню']  # Возврат в ГЛАВНОЕ меню
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_address_keyboard():
    """Меню управления адресами"""
    keyboard = [
        ['🏠 Добавить адрес'],
        ['↩️ Назад в меню']  # Возврат в ГЛАВНОЕ меню
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard():
    """Клавиатура для отмены операций"""
    keyboard = [['↩️ Отмена']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)