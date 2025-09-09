def update_user_subscription(user_id, subscribed: bool, end_date=None):
    """Обновляет статус подписки пользователя"""
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
    """Получает товары в корзине пользователя"""
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