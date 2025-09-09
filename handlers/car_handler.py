from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_user_car, get_user_cars
from keyboards import get_profile_keyboard, get_main_menu_keyboard, get_cars_keyboard, get_cancel_keyboard

async def show_user_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать автомобили пользователя"""
    user_id = update.effective_user.id
    cars = get_user_cars(user_id)
    
    if not cars:
        await update.message.reply_text(
            "🚗 У вас пока нет добавленных автомобилей.\n\n"
            "Нажмите 'Добавить автомобиль' чтобы добавить первый автомобиль.",
            reply_markup=get_cars_keyboard()
        )
        return
    
    cars_text = "🚗 <b>Ваши автомобили:</b>\n\n"
    for car in cars:
        car_id, user_id, brand, model, year = car
        cars_text += f"• {brand} {model} ({year} год)\n"
    
    await update.message.reply_text(
        cars_text,
        parse_mode='HTML',
        reply_markup=get_cars_keyboard()
    )

async def start_adding_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления автомобиля"""
    context.user_data['adding_car'] = True
    context.user_data['car_step'] = 'brand'
    
    await update.message.reply_text(
        "🚗 <b>Добавление автомобиля</b>\n\n"
        "Введите марку автомобиля (например: Geely, Chery, Haval):",
        parse_mode='HTML',
        reply_markup=get_cancel_keyboard()
    )

async def handle_car_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода марки автомобиля"""
    if update.message.text == '↩️ Отмена':
        await cancel_adding_car(update, context)
        return
    
    context.user_data['car_brand'] = update.message.text
    context.user_data['car_step'] = 'model'
    
    await update.message.reply_text(
        "Теперь введите модель автомобиля (например: Coolray, Tiggo 7, Jolion):",
        reply_markup=get_cancel_keyboard()
    )

async def handle_car_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода модели автомобиля"""
    if update.message.text == '↩️ Отмена':
        await cancel_adding_car(update, context)
        return
    
    context.user_data['car_model'] = update.message.text
    context.user_data['car_step'] = 'year'
    
    await update.message.reply_text(
        "Теперь введите год выпуска (например: 2022):",
        reply_markup=get_cancel_keyboard()
    )

async def handle_car_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода года выпуска и сохранение автомобиля"""
    if update.message.text == '↩️ Отмена':
        await cancel_adding_car(update, context)
        return
    
    try:
        year = int(update.message.text)
        user_id = update.effective_user.id
        brand = context.user_data.get('car_brand', '')
        model = context.user_data.get('car_model', '')
        
        if not brand or not model:
            await update.message.reply_text(
                "❌ Ошибка: данные неполные. Начните заново.",
                reply_markup=get_cars_keyboard()
            )
            await cancel_adding_car(update, context)
            return
        
        success = add_user_car(user_id, brand, model, year)
        
        if success:
            await update.message.reply_text(
                f"✅ Автомобиль успешно добавлен!\n\n"
                f"<b>Марка:</b> {brand}\n"
                f"<b>Модель:</b> {model}\n"
                f"<b>Год:</b> {year}",
                parse_mode='HTML',
                reply_markup=get_cars_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при добавлении автомобиля",
                reply_markup=get_cars_keyboard()
            )
            
    except ValueError:
        await update.message.reply_text(
            "❌ Год должен быть числом. Введите корректный год (например: 2022):",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Очищаем данные
    await cancel_adding_car(update, context)

async def cancel_adding_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена процесса добавления автомобиля"""
    # Очищаем данные
    context.user_data.pop('adding_car', None)
    context.user_data.pop('car_step', None)
    context.user_data.pop('car_brand', None)
    context.user_data.pop('car_model', None)
    
    if update.message.text != '↩️ Отмена':
        await update.message.reply_text(
            "Операция добавления автомобиля завершена",
            reply_markup=get_cars_keyboard()
        )
    else:
        await update.message.reply_text(
            "Добавление автомобиля отменено",
            reply_markup=get_cars_keyboard()
        )