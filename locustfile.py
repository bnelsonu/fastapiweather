from locust import HttpUser, task, between
import random

CITY_POOL = [
    {"city": "SanJose", "lat": 9.9281, "lon": -84.0907, "weight": 40},
    {"city": "Cartago", "lat": 9.8644, "lon": -83.9194, "weight": 20},
    {"city": "Alajuela", "lat": 10.0163, "lon": -84.2116, "weight": 15},
    {"city": "Heredia", "lat": 9.9986, "lon": -84.1165, "weight": 10},
    {"city": "Turrialba", "lat": 9.90467, "lon": -83.68352, "weight": 10},
    {"city": "Limon", "lat": 9.9907, "lon": -83.0350, "weight": 5},
]
cities = [c for c in CITY_POOL]
weights = [c["weight"] for c in CITY_POOL]


class WeatherUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def get_weather_mixed(self):
        c = random.choices(cities, weights=weights, k=1)[0]
        self.client.get(
            "/weather",
            params={
                "city": c["city"],
                "lat": c["lat"],
                "lon": c["lon"],
            },
            name="/weather (mixed-city)",
        )
