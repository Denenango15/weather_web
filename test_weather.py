import unittest
from unittest.mock import patch, Mock
from app import app, get_coordinates, get_weather_data

class TestWeatherApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('app.flash')
    def test_city_not_found(self, mock_flash):
        with patch('app.get_coordinates', return_value=(None, None)):
            response = self.app.post('/', data={'city': 'NonexistentCity'})
            self.assertEqual(response.status_code, 200)
            mock_flash.assert_called_once_with('Error: City not found', 'error')

    @patch('app.get_coordinates', return_value=(55.7558, 37.6176))
    @patch('app.get_weather_data')
    def test_weather_data(self, mock_get_weather_data, mock_get_coordinates):
        mock_get_weather_data.return_value = {
            'temperature': 20,
            'temperature_min': 15,
            'temperature_max': 25
        }
        response = self.app.post('/', data={'city': 'Moscow'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Moscow', response.data)
        self.assertIn(b'20', response.data)
        self.assertIn(b'15', response.data)
        self.assertIn(b'25', response.data)

    @patch('app.get_coordinates')
    @patch('app.requests.get')
    def test_get_coordinates(self, mock_get, mock_get_coordinates):
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {'latitude': 55.7558, 'longitude': 37.6176}
            ]
        }
        mock_get.return_value = mock_response

        lat, lon = get_coordinates('Moscow')
        self.assertEqual(lat, 55.7558)
        self.assertEqual(lon, 37.6176)

    @patch('app.requests.get')
    def test_get_weather_data(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'hourly': {'temperature_2m': [20]},
            'daily': {
                'temperature_2m_min': [15],
                'temperature_2m_max': [25]
            }
        }
        mock_get.return_value = mock_response

        weather_data = get_weather_data(55.7558, 37.6176)
        self.assertEqual(weather_data['temperature'], 20)
        self.assertEqual(weather_data['temperature_min'], 15)
        self.assertEqual(weather_data['temperature_max'], 25)

    def test_clear_cities(self):
        with self.app.session_transaction() as sess:
            sess['cities'] = ['Moscow']

        response = self.app.get('/clear_cities')
        self.assertEqual(response.status_code, 302)
        with self.app.session_transaction() as sess:
            self.assertNotIn('cities', sess)

    def test_get_coordinates_api(self):
        with patch('app.get_coordinates', return_value=(55.7558, 37.6176)):
            response = self.app.get('/get_coordinates?city=Moscow')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['lat'], 55.7558)
            self.assertEqual(data['lon'], 37.6176)

    def test_get_weather_data_api(self):
        with patch('app.get_weather_data', return_value={
            'temperature': 20,
            'temperature_min': 15,
            'temperature_max': 25
        }):
            response = self.app.get('/get_weather_data?lat=55.7558&lon=37.6176')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['temperature'], 20)
            self.assertEqual(data['temperature_min'], 15)
            self.assertEqual(data['temperature_max'], 25)

if __name__ == '__main__':
    unittest.main()
