from app.db.models import City, WeatherRecord
from sqlalchemy.future import select


async def get_or_create_city(db, name, country):
    result = await db.execute(
        select(City)
        .where(City.name == name, City.country == country)
        .order_by(City.id.asc())
    )
    city = result.scalars().first()

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
        description="N/A",
    )

    db.add(record)
    await db.commit()
    return record
