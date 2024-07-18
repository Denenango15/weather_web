from flask import Flask, render_template, request, flash, make_response, url_for, redirect
import requests

app = Flask(__name__)
app.secret_key = 'weccvev32r2fwc'


@app.route('/', methods=['GET', 'POST'])
def weather():
    cities = get_cities_from_cookie()

    if request.method == 'POST':
        city = request.form['city']
        lat, lon = get_coordinates(city)

        if lat is None or lon is None:
            flash(f"Error: City not found", "error")
        else:
            weather_data = get_weather_data(lat, lon)

            info = {
                'city': city,
                'temp': weather_data['temperature'],
                'temp_min': weather_data['temperature_min'],
                'temp_max': weather_data['temperature_max']
            }

            # Добавляем город в список городов
            if city not in cities:
                cities.append(city)

            # Сохраняем список городов в cookie на 30 дней
            response = make_response(render_template('index.html', info=info, cities=cities))
            response.set_cookie('cities', ','.join(cities), max_age=30 * 24 * 60 * 60)
            return response

    return render_template('index.html', cities=cities)


def get_cities_from_cookie():
    '''
    получаем куки

    '''
    cities_str = request.cookies.get('cities')
    if cities_str:
        return cities_str.split(',')
    else:
        return []


def get_coordinates(city):
    '''
    Получаем координаты
    '''
    api_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1'
    response = requests.get(api_url)
    data = response.json()

    results = data.get('results')
    if results and len(results) > 0:
        return results[0]['latitude'], results[0]['longitude']
    else:
        return None, None


def get_weather_data(lat, lon):
    '''
    Получаем информацию о погоде (текущую, минимальную и максимальную температуры)
    '''

    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&daily=temperature_2m_max,temperature_2m_min&timezone=auto'
    response = requests.get(api_url)
    data = response.json()

    current_temp = data['hourly']['temperature_2m'][0]
    temp_min = data['daily']['temperature_2m_min'][0]
    temp_max = data['daily']['temperature_2m_max'][0]

    return {
        'temperature': current_temp,
        'temperature_min': temp_min,
        'temperature_max': temp_max
    }


if __name__ == '__main__':
    app.run(debug=True)
