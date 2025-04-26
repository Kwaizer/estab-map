from datetime import datetime

from flask import Flask, render_template
import folium

app = Flask(__name__)


@app.route('/')
def index():
    # Створення мапи Одеси
    odessa_map = folium.Map(location=[46.4825, 30.7233], zoom_start=14)

    # Додавання маркеру для ресторанного комплексу
    folium.Marker(
        location=[46.4825, 30.7233],
        popup="ODESA STREET FOOD",
        tooltip="Хаджибейський район",
        icon=folium.Icon(color="red", icon="cutlery")
    ).add_to(odessa_map)

    # Генерація HTML для мапи
    map_html = odessa_map._repr_html_()

    return render_template("index.html", now=datetime.now())


@app.route('/restaurants/pizzeria')
def pizzeria():
    return render_template('restaurants/pizzeria.html')


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


if __name__ == '__main__':
    app.run(debug=True)