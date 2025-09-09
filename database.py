import sqlite3
from datetime import datetime, timedelta

def init_db():
    """Инициализация базы данных и создание таблиц"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()

    # Пользователи
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        subscribed BOOLEAN DEFAULT FALSE,
        subscription_end DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Автомобили пользователей
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # Адреса доставки
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        address TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # Товары (наша "витрина") - ДОБАВЬТЕ НЕСКОЛЬКО ТЕСТОВЫХ ТОВАРОВ
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parts (
        article TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        category TEXT,
        in_stock BOOLEAN DEFAULT TRUE
    )
    """)

    # Корзина
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        article TEXT,
        quantity INTEGER DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (article) REFERENCES parts (article)
    )
    """)

    # Избранное
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        user_id INTEGER,
        article TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, article),
        FOREIGN KEY (user_id) REFERENCES users (user_id),
        FOREIGN KEY (article) REFERENCES parts (article)
    )
    """)

    # Заказы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        status TEXT DEFAULT 'новый',
        total_amount REAL,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # Содержимое заказов
    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        article TEXT,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (article) REFERENCES parts (article)
    )
    """)

    # Добавляем тестовые товары
    test_parts = [
        ('ABC123', 'Тормозные колодки', 'Передние тормозные колодки для Geely', 4500.0, 'Тормозная система', True),
        ('DEF456', 'Масляный фильтр', 'Фильтр масляный универсальный', 1200.0, 'Фильтры', True),
        ('GHI789', 'Воздушный фильтр', 'Фильтр воздушный салонный', 850.0, 'Фильтры', True),
        ('JKL012', 'Свечи зажигания', 'Свечи иридиевые', 3200.0, 'Двигатель', True),
        ('MNO345', 'Ремень ГРМ', 'Ремень газораспределительного механизма', 2800.0, 'Двигатель', True)
    ]

    cur.executemany("""
    INSERT OR IGNORE INTO parts (article, name, description, price, category, in_stock)
    VALUES (?, ?, ?, ?, ?, ?)
    """, test_parts)

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована успешно!")

def get_user(user_id):
    """Получить пользователя по ID"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def add_user(user_id, username, first_name, last_name):
    """Добавить нового пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                (user_id, username, first_name, last_name))
    conn.commit()
    conn.close()

def update_user_subscription(user_id, subscribed: bool, end_date=None):
    """Обновить статус подписки пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    if end_date:
        cur.execute("UPDATE users SET subscribed = ?, subscription_end = ? WHERE user_id = ?",
                    (subscribed, end_date, user_id))
    else:
        cur.execute("UPDATE users SET subscribed = ? WHERE user_id = ?",
                    (subscribed, user_id))
    conn.commit()
    conn.close()

def get_user_cart_items(user_id):
    """Получить товары в корзине пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, p.article, p.name, p.price, c.quantity 
        FROM cart c 
        JOIN parts p ON c.article = p.article 
        WHERE c.user_id = ?
    """, (user_id,))
    items = cur.fetchall()
    conn.close()
    return items

def add_to_cart(user_id, article, quantity=1):
    """Добавить товар в корзину"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO cart (user_id, article, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, article) DO UPDATE SET quantity = quantity + ?
        """, (user_id, article, quantity, quantity))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def search_parts(query):
    """Поиск товаров по артикулу или названию"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT article, name, price, in_stock 
        FROM parts 
        WHERE article LIKE ? OR name LIKE ? 
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))
    results = cur.fetchall()
    conn.close()
    return results

# Добавьте эту функцию для отдельного запуска инициализации БД
if __name__ == "__main__":
    init_db()
    print("База данных создана. Добавлено тестовых товаров: 5")

  # Добавьте эти функции в конец database.py

def add_to_cart_db(user_id, article, quantity=1):
    """Добавить товар в корзину (алиас для add_to_cart)"""
    return add_to_cart(user_id, article, quantity)

def update_cart_item(item_id, quantity):
    """Обновить количество товара в корзине"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        if quantity <= 0:
            cur.execute("DELETE FROM cart WHERE id = ?", (item_id,))
        else:
            cur.execute("UPDATE cart SET quantity = ? WHERE id = ?", (quantity, item_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def delete_cart_item(item_id):
    """Удалить товар из корзины"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cart WHERE id = ?", (item_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def clear_user_cart(user_id):
    """Очистить корзину пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_part_by_article(article):
    """Получить товар по артикулу"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts WHERE article = ?", (article,))
    part = cur.fetchone()
    conn.close()
    return part

def add_user_car(user_id, brand, model, year):
    """Добавить автомобиль пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO user_cars (user_id, brand, model, year) VALUES (?, ?, ?, ?)",
                    (user_id, brand, model, year))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_user_cars(user_id):
    """Получить автомобили пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_cars WHERE user_id = ?", (user_id,))
    cars = cur.fetchall()
    conn.close()
    return cars

def add_user_address(user_id, address):
    """Добавить адрес пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO user_addresses (user_id, address) VALUES (?, ?)",
                    (user_id, address))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_user_addresses(user_id):
    """Получить адреса пользователя"""
    conn = sqlite3.connect('bot_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_addresses WHERE user_id = ?", (user_id,))
    addresses = cur.fetchall()
    conn.close()
    return addresses