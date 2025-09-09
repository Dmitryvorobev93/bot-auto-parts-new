from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from database import search_parts, add_to_cart
from decorators import check_subscription
from keyboards import get_main_menu_keyboard

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало поиска"""
    # Устанавливаем флаг режима поиска
    context.user_data['search_mode'] = True
    await update.message.reply_text(
        "🔍 Введите артикул или название запчасти:\n\n"
        "Например: 'тормозные колодки' или 'ABC123'\n\n"
        "Для выхода из поиска нажмите '↩️ Назад в меню'",
        reply_markup=get_main_menu_keyboard()
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка поискового запроса"""
    search_query = update.message.text
    
    # НЕ сбрасываем режим поиска - оставляем активным для следующих запросов
    # context.user_data['search_mode'] = False  ← ЭТУ СТРОКУ УБИРАЕМ!
    
    results = search_parts(search_query)
    
    if not results:
        await update.message.reply_text(
            "😔 Ничего не найдено. Попробуйте другой запрос.\n\n"
            "Продолжайте вводить запросы для поиска...",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    for item in results:
        article, name, price, in_stock = item
        keyboard = []
        
        if in_stock:
            keyboard.append([InlineKeyboardButton("➕ В корзину", callback_data=f"add_{article}")])
        
        # Добавляем кнопку возврата к поиску
        keyboard.append([InlineKeyboardButton("🔍 Новый поиск", callback_data="new_search")])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        text = f"""🔹 {name}
📦 Артикул: {article}
💰 Цена: {price} руб.
{'✅ В наличии' if in_stock else '❌ Нет в наличии'}"""
        
        await update.message.reply_text(text, reply_markup=reply_markup)

@check_subscription
async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка callback-кнопок поиска"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "new_search":
        # Возврат к поиску - просто отправляем сообщение
        await query.message.reply_text(
            "🔍 Введите артикул или название запчасти для нового поиска:",
            reply_markup=get_main_menu_keyboard()
        )
        # Устанавливаем режим поиска
        context.user_data['search_mode'] = True
        return
    
    # Обработка добавления в корзину
    if query.data.startswith("add_"):
        article = query.data.split("_")[1]
        user_id = query.from_user.id
        
        success = add_to_cart(user_id, article)
        
        if success:
            await query.answer("✅ Добавлено в корзину!")
        else:
            await query.answer("❌ Ошибка добавления", show_alert=True)