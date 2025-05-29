import os
import sqlite3
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
import folium
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY') # Замените на случайную строку

# Конфигурация аутентификации
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

load_dotenv()
# Настройки для Gmail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

def location():
    # Координати ресторанного комплексу
    latitude = 46.4825
    longitude = 30.7233

    # Створення карти
    odessa_map = folium.Map(location=[latitude, longitude], zoom_start=13)

    # Створення HTML-посилання
    popup_html = f'<a href="https://www.google.com/maps?q={latitude},{longitude}" target="_blank">Відкрити в Google Maps</a>'

    # Додавання маркеру
    folium.Marker(
        location=[latitude, longitude],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip="Хаджибейський район",
        icon=folium.Icon(color="red", icon="cutlery")
    ).add_to(odessa_map)

    # Генерація HTML для мапи
    return odessa_map._repr_html_()

@app.route('/')
def index():
    return render_template("index.html", now=datetime.now(), map_html=location())


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            flash("Будь ласка, увійдіть для доступу до цієї сторінки", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            flash("Ви успішно увійшли", "success")
            return redirect(url_for("admin"))
        else:
            flash("Невірний логін або пароль", "error")

    return render_template("admin_login.html", now=datetime.now())


@app.route("/admin/logout")
def admin_logout():
    session.pop("logged_in", None)
    flash("Ви вийшли з системи", "info")
    return redirect(url_for("admin_login"))


@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html", now=datetime.now(), map_html=location())

def get_news():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY date DESC")
    news_items = [dict(zip(['id', 'title', 'date', 'content', 'image'], row)) for row in c.fetchall()]
    conn.close()
    return news_items

@app.route('/news')
def news():
    news_items = get_news()
    return render_template('news.html', now=datetime.now(), news_items=news_items)

@app.route('/news/<int:news_id>')
def news_item(news_id):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM news WHERE id = ?", (news_id,))
    news_item = dict(zip(['id', 'title', 'date', 'content', 'image'], c.fetchone()))
    conn.close()
    return render_template('news_item.html', now=datetime.now(), news_item=news_item)


@app.route('/admin/news')
def admin_news():
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY date DESC")
    news_items = [dict(zip(['id', 'title', 'date', 'content', 'image'], row)) for row in c.fetchall()]
    conn.close()
    return render_template('admin_news.html', now=datetime.now(), news_items=news_items)


# Конфигурация загрузки файлов
UPLOAD_FOLDER = 'static/images/news'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/news/add', methods=['GET', 'POST'])
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        content = request.form['content']

        # Обработка загрузки файла
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('news.db')
        c = conn.cursor()
        c.execute("INSERT INTO news (title, date, content, image) VALUES (?, ?, ?, ?)",
                  (title, date, content, filename))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_news'))

    return render_template('add_news.html', now=datetime.now(), today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/admin/news/edit/<int:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        content = request.form['content']

        # Обработка загрузки файла
        filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if filename:
            c.execute("UPDATE news SET title=?, date=?, content=?, image=? WHERE id=?",
                      (title, date, content, filename, news_id))
        else:
            c.execute("UPDATE news SET title=?, date=?, content=? WHERE id=?",
                      (title, date, content, news_id))

        conn.commit()
        conn.close()
        return redirect(url_for('admin_news'))

    c.execute("SELECT * FROM news WHERE id=?", (news_id,))
    news_item = dict(zip(['id', 'title', 'date', 'content', 'image'], c.fetchone()))
    conn.close()

    return render_template('edit_news.html', now=datetime.now(), news_item=news_item, today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/admin/news/delete/<int:news_id>')
def delete_news(news_id):
    conn = sqlite3.connect('news.db')
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE id=?", (news_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_news'))

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']
        print(email)
        msg = Message(subject="Повідомлення з форми ODESA STREET FOOD",
                      recipients=['testytestlpambuk@gmail.com'])
        msg.body = f"Ім’я: {name}\nEmail: {email}\n\nПовідомлення:\n{message_text}"
        try:
            mail.send(msg)
            flash('Повідомлення успішно надіслано!', 'success')
        except Exception as e:
            print("Email error:", e)
            flash('Сталася помилка при відправленні.', 'error')

        return redirect('/contacts')

    return render_template('contacts.html', now=datetime.now(), map_html=location())

@app.route('/restaurants')
def restaurants():
    return render_template('restaurants.html', now=datetime.now())

@app.route('/restaurants/pizzeria')
def pizzeria():
    return render_template('restaurants/pizzeria.html', now=datetime.now())

@app.route('/restaurants/fish_bistro')
def  fish_bistro():
    return render_template('restaurants/fish-bistro.html', now=datetime.now())

@app.route('/restaurants/grill_bar')
def grill_bar():
    return render_template('restaurants/grill-bar.html', now=datetime.now())

@app.route('/restaurants/beer_garden')
def beer_garden():
    return render_template('restaurants/beer-garden.html', now=datetime.now())

@app.route('/restaurants/halushki')
def halushki():
    return render_template('restaurants/halushki.html', now=datetime.now())

@app.route('/restaurants/georgian')
def georgian():
    return render_template('restaurants/georgian.html', now=datetime.now())

@app.route('/restaurants/burgers')
def burgers():
    return render_template('restaurants/burgers.html', now=datetime.now())

@app.route('/restaurants/dumplings')
def dumplings():
    return render_template('restaurants/dumplings.html', now=datetime.now())

@app.route('/restaurants/hotdog')
def hotdog():
    return render_template('restaurants/hotdog.html', now=datetime.now())

@app.route('/restaurants/cheburek')
def cheburek():
    return render_template('restaurants/cheburek.html', now=datetime.now())

@app.route('/restaurants/pancakes')
def pancakes():
    return render_template('restaurants/pancakes.html', now=datetime.now())

@app.route('/restaurants/confectionery')
def confectionery():
    return render_template('restaurants/confectionery.html', now=datetime.now())

@app.route('/restaurants/donuts')
def donuts():
    return render_template('restaurants/donuts.html', now=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)
