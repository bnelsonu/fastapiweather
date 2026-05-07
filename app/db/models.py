from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


# Represents a city for which weather data can be fetched and stored.
# One city can have many associated weather records (one-to-many).
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)  # Auto-incremented primary key
    name = Column(String)  # City name, e.g. "Cartago"
    country = Column(String)  # Country code or name, e.g. "CR"

    # Back-reference to all weather records linked to this city
    weather_records = relationship("WeatherRecord", back_populates="city")


# Stores a single weather snapshot for a city at a given point in time.
# Each record belongs to exactly one city via a foreign key.
class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True)  # Auto-incremented primary key
    city_id = Column(Integer, ForeignKey("cities.id"))  # FK to the cities table
    temperature = Column(Float)  # Temperature in °C
    humidity = Column(Float)  # Relative humidity (%)
    description = Column(String)  # Weather description, e.g. "Clear"
    timestamp = Column(DateTime, default=datetime.utcnow)  # UTC time of the record

    # Reference back to the parent City object
    city = relationship("City", back_populates="weather_records")
