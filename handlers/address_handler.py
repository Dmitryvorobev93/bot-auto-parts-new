from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_user_address, get_user_addresses
from keyboards import get_profile_keyboard, get_main_menu_keyboard, get_address_keyboard, get_cancel_keyboard

async def show_user_addresses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать адреса пользователя"""
    user_id = update.effective_user.id
    addresses = get_user_addresses(user_id)
    
    if not addresses:
        await update.message.reply_text(
            "🏠 У вас пока нет добавленных адресов.\n\n"
            "Нажмите 'Добавить адрес' чтобы добавить первый адрес доставки.",
            reply_markup=get_address_keyboard()
        )
        return
    
    addresses_text = "🏠 <b>Ваши адреса:</b>\n\n"
    for address in addresses:
        addr_id, user_id, address_text = address
        addresses_text += f"• {address_text}\n"
    
    await update.message.reply_text(
        addresses_text,
        parse_mode='HTML',
        reply_markup=get_address_keyboard()
    )

async def start_adding_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления адреса"""
    context.user_data['adding_address'] = True
    
    await update.message.reply_text(
        "🏠 <b>Добавление адреса</b>\n\n"
        "Введите ваш адрес для доставки:\n\n"
        "Формат: Город, улица, дом, квартира\n"
        "Например: Москва, ул. Ленина, д. 15, кв. 42",
        parse_mode='HTML',
        reply_markup=get_cancel_keyboard()
    )

async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода адреса"""
    if update.message.text == '↩️ Отмена':
        await cancel_adding_address(update, context)
        return
    
    address = update.message.text.strip()
    user_id = update.effective_user.id
    
    if len(address) < 10:
        await update.message.reply_text(
            "❌ Адрес слишком короткий. Введите полный адрес:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    success = add_user_address(user_id, address)
    
    if success:
        await update.message.reply_text(
            f"✅ Адрес успешно добавлен:\n{address}",
            reply_markup=get_address_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при добавлении адреса",
            reply_markup=get_address_keyboard()
        )
    
    # Очищаем данные
    await cancel_adding_address(update, context)

async def cancel_adding_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена процесса добавления адреса"""
    context.user_data.pop('adding_address', None)
    
    if update.message.text != '↩️ Отмена':
        await update.message.reply_text(
            "Операция добавления адреса завершена",
            reply_markup=get_address_keyboard()
        )
    else:
        await update.message.reply_text(
            "Добавление адреса отменено",
            reply_markup=get_address_keyboard()
        )