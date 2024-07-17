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
});
