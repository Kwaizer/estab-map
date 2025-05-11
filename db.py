# db.py
import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    # Создаем таблицу новостей
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  date TEXT NOT NULL,
                  content TEXT NOT NULL,
                  image TEXT NOT NULL)''')

    # Добавляем тестовые данные, если таблица пуста
    c.execute("SELECT COUNT(*) FROM news")
    if c.fetchone()[0] == 0:
        news_items = [
            ('Фестиваль вуличної їжі', '15 травня 2023',
             'Запрошуємо на великий фестиваль вуличної їжі, де вас чекають смачні страви з усього світу, жива музика та майстер-класи від наших шеф-кухарів.',
             'food-festival.jpg'),
            ('Нове меню в піцерії', '28 квітня 2023',
             'Ми оновили наше меню! Спробуйте нові авторські піци з сезонними інгредієнтами та особливими соусами власного приготування.',
             'new-menu.jpg'),
            ('Літній майданчик', '1 травня 2023',
             'Відкрилися наші літні майданчики з чудовим видом на море. Ідеальне місце для вечірніх зустрічей з друзями.',
             'summer-terrace.jpg')
        ]
        c.executemany("INSERT INTO news (title, date, content, image) VALUES (?, ?, ?, ?)", news_items)

    conn.commit()
    conn.close()


init_db()