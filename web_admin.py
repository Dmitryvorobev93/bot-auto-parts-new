from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Пароль для доступа (замените на свой)
ADMIN_PASSWORD = "admin123"

def get_db_connection():
    """Подключение к базе данных"""
    conn = sqlite3.connect('bot_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Страница входа"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            return render_template('admin_panel.html')
        else:
            return "Неверный пароль", 401
    
    return '''
    <form method="post">
        <h2>Вход в админ-панель</h2>
        <input type="password" name="password" placeholder="Пароль" required>
        <button type="submit">Войти</button>
    </form>
    '''

@app.route('/admin/parts')
def get_parts():
    """Получить список товаров"""
    conn = get_db_connection()
    parts = conn.execute('SELECT * FROM parts').fetchall()
    conn.close()
    return jsonify([dict(part) for part in parts])

@app.route('/admin/parts/add', methods=['POST'])
def add_part():
    """Добавить товар"""
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute('''
            INSERT INTO parts (article, name, description, price, category, in_stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['article'], data['name'], data['description'], 
              data['price'], data['category'], data.get('in_stock', True)))
        
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

@app.route('/admin/parts/update/<article>', methods=['POST'])
def update_part(article):
    """Обновить товар"""
    data = request.json
    conn = get_db_connection()
    
    try:
        conn.execute('''
            UPDATE parts 
            SET name = ?, description = ?, price = ?, category = ?, in_stock = ?
            WHERE article = ?
        ''', (data['name'], data['description'], data['price'], 
              data['category'], data.get('in_stock', True), article))
        
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

@app.route('/admin/parts/delete/<article>', methods=['DELETE'])
def delete_part(article):
    """Удалить товар"""
    conn = get_db_connection()
    
    try:
        conn.execute('DELETE FROM parts WHERE article = ?', (article,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

if __name__ == '__main__':
    # Создаем папку для шаблонов
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Запускаем веб-сервер
    app.run(debug=True, port=5000)