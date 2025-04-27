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
@app.route('/')
def index():
    return render_template("index.html", now=datetime.now(), map_html=location())

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html', map_html=location())

@app.route('/restaurants')
def restaurants():
    return render_template('restaurants.html')

@app.route('/restaurants/pizzeria')
def pizzeria():
    return render_template('restaurants/pizzeria.html')



if __name__ == '__main__':
    app.run(debug=True)