from datetime import datetime

from flask import Flask, render_template
import folium

app = Flask(__name__)

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

# Приклад даних новин (можна замінити на дані з БД)
news_items = [
    {
        'title': 'Фестиваль вуличної їжі',
        'date': '15 травня 2023',
        'content': 'Запрошуємо на великий фестиваль вуличної їжі, де вас чекають смачні страви з усього світу, жива музика та майстер-класи від наших шеф-кухарів.',
        'image': 'food-festival.jpg'
    },
    {
        'title': 'Нове меню в піцерії',
        'date': '28 квітня 2023',
        'content': 'Ми оновили наше меню! Спробуйте нові авторські піци з сезонними інгредієнтами та особливими соусами власного приготування.',
        'image': 'new-menu.jpg'
    },
    {
        'title': 'Літній майданчик',
        'date': '1 травня 2023',
        'content': 'Відкрилися наші літні майданчики з чудовим видом на море. Ідеальне місце для вечірніх зустрічей з друзями.',
        'image': 'summer-terrace.jpg'
    }
]
@app.route('/')
def index():
    return render_template("index.html", now=datetime.now(), map_html=location())

@app.route('/news')
def news():
    return render_template('news.html', now=datetime.now(), news_items=news_items)

@app.route('/contacts')
def contacts():
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



if __name__ == '__main__':
    app.run(debug=True)