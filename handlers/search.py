from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import search_parts, add_to_cart_db
from decorators import check_subscription

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало поиска (доступно всем)"""
    await update.message.reply_text("🔍 Введите артикул или название запчасти:")

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка поискового запроса (доступно всем)"""
    search_query = update.message.text
    results = search_parts(search_query)
    
    if not results:
        await update.message.reply_text("😔 Ничего не найдено")
        return
    
    # Показываем результаты поиска
    for item in results:
        article, name, price, in_stock = item
        keyboard = []
        
        if in_stock:
            # Кнопка "В корзину" требует подписки
            keyboard.append([InlineKeyboardButton("➕ В корзину", callback_data=f"add_{article}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        text = f"🔹 {name}\n📦 Артикул: {article}\n💰 Цена: {price} руб.\n{'✅ В наличии' if in_stock else '❌ Нет в наличии'}"
        await update.message.reply_text(text, reply_markup=reply_markup)

@check_subscription
async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление в корзину (только для подписанных)"""
    query = update.callback_query
    await query.answer()
    
    article = query.data.split("_")[1]
    user_id = query.from_user.id
    
    # Добавляем товар в корзину
    success = add_to_cart_db(user_id, article)
    
    if success:
        await query.answer("✅ Добавлено в корзину!")
    else:
        await query.answer("❌ Ошибка добавления", show_alert=True)