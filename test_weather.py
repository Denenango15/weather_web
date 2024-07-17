import unittest
from app import app, get_coordinates, get_weather_data

class TestWeatherApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_city_not_found(self):
        response = self.app.post('/', data={'city': 'NonexistentCity'})
        self.assertEqual(response.status_code, 400)

    def test_get_coordinates(self):
        lat, lon = get_coordinates('Moscow')
        self.assertIsNotNone(lat)
        self.assertIsNotNone(lon)

    def test_get_weather_data(self):
        lat, lon = get_coordinates('Moscow')
        weather_data = get_weather_data(lat, lon)

        self.assertIn('temperature', weather_data)
        self.assertIn('temperature_min', weather_data)
        self.assertIn('temperature_max', weather_data)

if __name__ == '__main__':
    unittest.main()
