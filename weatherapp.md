# FastAPI Concurrency & Parallelism Project (Weather API + PostgreSQL)

## 🎯 Goal

Build a real-world project to understand:

* Concurrency (async/await)
* Parallelism (workers/processes)
* External API consumption
* Async DB writes
* Performance testing under load

---

## 🧠 Concepts

### Concurrency

Handle multiple tasks at once without blocking (I/O bound)

* API calls
* DB queries

### Parallelism

Execute tasks at the same time (CPU bound)

* Multiple processes (workers)

---

## 🏗️ Project Structure

```
app/
 ├── main.py
 ├── db/
 │    ├── session.py
 │    ├── models.py
 │    └── schemas.py
 ├── services/
 │    └── weather_service.py
 ├── repositories/
 │    └── weather_repository.py
```

---

## 🗄️ Database Design

### Table: cities

* id (PK)
* name
* country

### Table: weather_records

* id (PK)
* city_id (FK)
* temperature
* humidity
* description
* timestamp

Relationship:

* One city → many weather records

---

## ⚙️ Dependencies

```bash
pip install fastapi uvicorn httpx sqlalchemy asyncpg psycopg2-binary
```

---

## 🔌 Async DB Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:securepassword@localhost:5434/weather_db"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

---

## 🧱 Models

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    country = Column(String)

    weather_records = relationship("WeatherRecord", back_populates="city")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    temperature = Column(Float)
    humidity = Column(Float)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    city = relationship("City", back_populates="weather_records")
```

---

## 🌦️ Weather Service (Async API Call)

```python
import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"

async def fetch_weather(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            BASE_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            }
        )
        return response.json()
```

---

## 💾 Repository Layer

```python
from db.models import City, WeatherRecord
from sqlalchemy.future import select

async def get_or_create_city(db, name, country):
    result = await db.execute(
        select(City).where(City.name == name)
    )
    city = result.scalar_one_or_none()

    if city:
        return city

    city = City(name=name, country=country)
    db.add(city)
    await db.commit()
    await db.refresh(city)

    return city


async def save_weather(db, city_id, weather_data):
    record = WeatherRecord(
        city_id=city_id,
        temperature=weather_data["temperature"],
        humidity=weather_data.get("relativehumidity", 0),
        description="N/A"
    )

    db.add(record)
    await db.commit()
    return record
```

---

## 🚀 FastAPI Endpoint

```python
from fastapi import FastAPI, Depends
from db.session import AsyncSessionLocal
from services.weather_service import fetch_weather
from repositories.weather_repository import get_or_create_city, save_weather

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/weather")
async def get_weather(city: str, lat: float, lon: float, db=Depends(get_db)):
    weather_response = await fetch_weather(lat, lon)

    current = weather_response["current_weather"]

    city_obj = await get_or_create_city(db, city, "CR")

    await save_weather(
        db,
        city_obj.id,
        {
            "temperature": current["temperature"],
            "relativehumidity": 50
        }
    )

    return {
        "city": city,
        "temperature": current["temperature"]
    }
```

---

## ⚡ Running the App

### 1. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 2. Make a single request

**Using curl:**

```bash
curl "http://localhost:8000/weather?city=Cartago&lat=9.8644&lon=-83.9194"
```

**Using httpx in Python:**

```python
import httpx

response = httpx.get(
    "http://localhost:8000/weather",
    params={"city": "Cartago", "lat": 9.8644, "lon": -83.9194}
)
print(response.json())
```

**Expected response:**

```json
{
  "city": "Cartago",
  "temperature": 18.5
}
```

### 3. Interactive API docs

Open your browser at `http://localhost:8000/docs` to explore the API via Swagger UI.

---

## 📊 Load Testing

### Option 1: hey

```bash
hey -n 1000 -c 50 "http://localhost:8000/weather?city=Cartago&lat=9.8644&lon=-83.9194"
```

### Option 2: locust

```bash
pip install locust
```

```python
from locust import HttpUser, task

class WeatherUser(HttpUser):

    @task
    def get_weather(self):
        self.client.get(
            "/weather?city=Cartago&lat=9.8644&lon=-83.9194"
        )
```

```bash
locust
```

---

## 📈 What to Measure

* Response time
* Requests per second
* Error rate

---

## 🧠 Key Interview Insights

### Why async?

* External API calls are I/O bound
* DB operations are I/O bound

### Bottlenecks

* DB connections
* External API latency

### Improvements

* Add caching (Redis)
* Bulk inserts
* Retry logic
* Background workers

---

## 🚀 Next Steps

* Add connection pooling tuning
* Compare sync vs async versions
* Add circuit breaker pattern
* Simulate API failures
* Add metrics (Prometheus + Grafana)

---

## ✅ Summary

This project demonstrates:

* Real async API consumption
* Async DB operations
* Concurrency under load
* Clean architecture separation

Perfect for backend interviews focused on FastAPI and system design.
