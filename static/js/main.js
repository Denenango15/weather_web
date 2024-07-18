document.addEventListener("DOMContentLoaded", function () {
  const cityInput = document.getElementById("city");
  const citySuggestions = document.getElementById("city-suggestions");

  async function fetchCitySuggestions(query, language) {
    const response = await fetch(
      `https://geocoding-api.open-meteo.com/v1/search?name=${query}&language=${language}&count=10`
    );
    const data = await response.json();
    return data.results.map((result) => result.name);
  }

  async function updateCitySuggestions() {
    const query = cityInput.value.trim();
    if (query.length === 0) {
      citySuggestions.innerHTML = "";
      return;
    }

    try {
      const [enSuggestions, ruSuggestions] = await Promise.all([
        fetchCitySuggestions(query, "en"),
        fetchCitySuggestions(query, "ru"),
      ]);
      const suggestions = [...new Set([...enSuggestions, ...ruSuggestions])];
      citySuggestions.innerHTML = suggestions
        .map((suggestion) => `<option value="${suggestion}">`)
        .join("");
    } catch (error) {
      console.error("Error fetching city suggestions:", error);
      citySuggestions.innerHTML = "";
    }
  }


  cityInput.addEventListener("input", updateCitySuggestions);

  document.querySelectorAll('ul li a').forEach(function (tab) {
    tab.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelectorAll('ul li a').forEach(function (tab) {
        tab.classList.remove('active');
      });
      this.classList.add('active');
      document.querySelectorAll('.tab').forEach(function (tabContent) {
        tabContent.classList.remove('active');
      });
      document.querySelector('.tab-content > div:nth-child(' + (Array.from(this.parentNode.parentNode.children).indexOf(this.parentNode) + 1) + ')').classList.add('active');
    });
  });

  async function updateWeatherInfo(city) {
    const weatherInfo = await getWeatherDataByCity(city);

    if (weatherInfo) {
      document.querySelector('h2').textContent = `${weatherInfo.city}:`;
      document.querySelector('p:nth-child(2)').textContent = `Текущая температура: ${weatherInfo.temp}°C`;
      document.querySelector('p:nth-child(3)').textContent = `Минимальная температура: ${weatherInfo.temp_min}°C`;
      document.querySelector('p:nth-child(4)').textContent = `Максимальная температура: ${weatherInfo.temp_max}°C`;
    }
  }

  document.querySelectorAll('.tab-content > div:nth-child(2) a').forEach(function (cityLink) {
    cityLink.addEventListener('click', async function (e) {
      e.preventDefault();
      const city = this.dataset.city;
      cityInput.value = city;
      const form = document.querySelector('form');
      const formData = new FormData(form);
      formData.set('city', city);

      const response = await fetch('/weather', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const info = await response.json();
        updateWeatherInfo(info);
      }
    });
  });

  const clearCitiesButton = document.getElementById("clear-cities");
  clearCitiesButton.addEventListener("click", function () {
    fetch('/clear_cities')
      .then(response => {
        if (response.ok) {
          location.reload();
        }
      });
  });

  async function getWeatherDataByCity(city) {
    const latLon = await fetch(`/get_coordinates?city=${city}`)
      .then((response) => response.json());

    if (latLon) {
      const weatherData = await fetch(`/get_weather_data?lat=${latLon.lat}&lon=${latLon.lon}`)
        .then((response) => response.json());

      return {
        city: city,
        temp: weatherData.temperature,
        temp_min: weatherData.temperature_min,
        temp_max: weatherData.temperature_max
      };
    } else {
      flash("Error: City not found", "error");
    }
  }

  const currentCity = document.querySelector('h2').textContent.slice(0, -1);
  if (currentCity) {
    updateWeatherInfo(currentCity);
  }
});
