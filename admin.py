from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, CommandHandler
import sqlite3
from config import ADMIN_IDS

def is_admin(user_id):
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

# Состояния для добавления/редактирования товаров
ADD_PART, EDIT_PART, DELETE_PART = range(3)
GET_ARTICLE, GET_NAME, GET_DESCRIPTION, GET_PRICE, GET_CATEGORY = range(5, 10)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ-панель"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Доступ запрещен")
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ Добавить товар", callback_data="admin_add_part")],
        [InlineKeyboardButton("✏️ Редактировать товар", callback_data="admin_edit_part")],
        [InlineKeyboardButton("🗑️ Удалить товар", callback_data="admin_delete_part")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("↩️ Назад", callback_data="admin_back")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👨‍💼 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def admin_add_part_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало добавления товара"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['admin_action'] = 'add_part'
    await query.message.reply_text("Введите артикул товара:")
    return GET_ARTICLE

async def admin_get_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение артикула"""
    context.user_data['part_article'] = update.message.text
    await update.message.reply_text("Введите название товара:")
    return GET_NAME

async def admin_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение названия"""
    context.user_data['part_name'] = update.message.text
    await update.message.reply_text("Введите описание товара:")
    return GET_DESCRIPTION

async def admin_get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение описания"""
    context.user_data['part_description'] = update.message.text
    await update.message.reply_text("Введите цену товара:")
    return GET_PRICE

async def admin_get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение цены"""
    try:
        price = float(update.message.text)
        context.user_data['part_price'] = price
        await update.message.reply_text("Введите категорию товара:")
        return GET_CATEGORY
    except ValueError:
        await update.message.reply_text("❌ Цена должна быть числом. Введите снова:")
        return GET_PRICE

async def admin_get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получение категории и сохранение товара"""
    category = update.message.text
    
    # Сохраняем товар в базу
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO parts (article, name, description, price, category, in_stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            context.user_data['part_article'],
            context.user_data['part_name'],
            context.user_data['part_description'],
            context.user_data['part_price'],
            category,
            True
        ))
        conn.commit()
        
        await update.message.reply_text(
            f"✅ Товар успешно добавлен!\n\n"
            f"Артикул: {context.user_data['part_article']}\n"
            f"Название: {context.user_data['part_name']}\n"
            f"Цена: {context.user_data['part_price']} руб."
        )
        
    except sqlite3.IntegrityError:
        await update.message.reply_text("❌ Товар с таким артикулом уже существует!")
    finally:
        conn.close()
    
    # Очищаем данные
    context.user_data.clear()
    return ConversationHandler.END

async def admin_edit_part_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало редактирования товара"""
    query = update.callback_query
    await query.answer()
    
    # Показываем список товаров для редактирования
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT article, name, price FROM parts LIMIT 10")
    parts = cursor.fetchall()
    conn.close()
    
    if not parts:
        await query.message.reply_text("❌ Нет товаров для редактирования")
        return ConversationHandler.END
    
    keyboard = []
    for part in parts:
        article, name, price = part
        keyboard.append([InlineKeyboardButton(f"{name} ({price} руб.)", callback_data=f"edit_{article}")])
    
    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="admin_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Выберите товар для редактирования:",
        reply_markup=reply_markup
    )

async def admin_show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику"""
    query = update.callback_query
    await query.answer()
    
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    
    # Статистика пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE subscribed = 1")
    subscribed_users = cursor.fetchone()[0]
    
    # Статистика товаров
    cursor.execute("SELECT COUNT(*) FROM parts")
    total_parts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM parts WHERE in_stock = 1")
    in_stock_parts = cursor.fetchone()[0]
    
    # Статистика заказов
    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status = 'completed'")
    total_revenue = cursor.fetchone()[0] or 0
    
    conn.close()
    
    stats_text = f"""
📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b>
• Всего: {total_users}
• С подпиской: {subscribed_users}

📦 <b>Товары:</b>
• Всего: {total_parts}
• В наличии: {in_stock_parts}

💰 <b>Заказы:</b>
• Всего: {total_orders}
• Общая выручка: {total_revenue} руб.
    """
    
    await query.message.reply_text(stats_text, parse_mode='HTML')

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена админ-действия"""
    context.user_data.clear()
    await update.message.reply_text("❌ Действие отменено")
    return ConversationHandler.END

async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат из админ-панели"""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Возврат в главное меню")