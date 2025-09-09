from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    keyboard = [
        ['🔍 Поиск запчастей'],
        ['🧺 Корзина', '❤️ Избранное'],
        ['👤 Личный кабинет', '🆘 Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_to_menu_keyboard():
    keyboard = [['↩️ Назад в меню']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_profile_keyboard():
    keyboard = [
        ['🚗 Мои автомобили', '🏠 Мой адрес'],
        ['💳 Купить подписку'],
        ['↩️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cart_keyboard(cart_items):
    # Динамическая клавиатура для корзины
    keyboard = []
    for item in cart_items:
        keyboard.append([
            InlineKeyboardButton(f"➖", callback_data=f"cart_dec_{item['id']}"),
            InlineKeyboardButton(f"{item['name']} x{item['quantity']}", callback_data=" "),
            InlineKeyboardButton(f"➕", callback_data=f"cart_inc_{item['id']}"),
            InlineKeyboardButton(f"❌", callback_data=f"cart_del_{item['id']}")
        ])
    keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)