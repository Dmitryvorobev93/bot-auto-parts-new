from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import get_user_cart_items, update_cart_item, delete_cart_item, clear_user_cart
from decorators import check_subscription
from keyboards import get_main_menu_keyboard

@check_subscription
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать корзину"""
    user_id = update.effective_user.id
    cart_items = get_user_cart_items(user_id)
    
    if not cart_items:
        await update.message.reply_text("🛒 Ваша корзина пуста", reply_markup=get_main_menu_keyboard())
        return
    
    keyboard = []
    total = 0
    
    for item in cart_items:
        item_id, article, name, price, quantity = item
        total += price * quantity
        
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"cart_dec_{item_id}"),
            InlineKeyboardButton(f"{name} x{quantity}", callback_data=" "),
            InlineKeyboardButton("➕", callback_data=f"cart_inc_{item_id}"),
            InlineKeyboardButton("❌", callback_data=f"cart_del_{item_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    cart_text = f"🛒 Ваша корзина:\n\nОбщая сумма: {total} руб."
    await update.message.reply_text(cart_text, reply_markup=reply_markup)

async def cart_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок корзины"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("cart_inc_"):
        item_id = int(data.split("_")[2])
        # Увеличиваем количество
        update_cart_item(item_id, 1)  # Просто добавляем 1
        await query.answer("Количество увеличено")
        
    elif data.startswith("cart_dec_"):
        item_id = int(data.split("_")[2])
        # Уменьшаем количество
        update_cart_item(item_id, -1)  # Уменьшаем на 1
        await query.answer("Количество уменьшено")
    
    elif data.startswith("cart_del_"):
        item_id = int(data.split("_")[2])
        delete_cart_item(item_id)
        await query.answer("Товар удален")
    
    elif data == "clear_cart":
        clear_user_cart(user_id)
        await query.answer("Корзина очищена")
        await query.edit_message_text("🗑 Корзина очищена")
        return
    
    # Обновляем сообщение корзины
    await show_cart(update, context)