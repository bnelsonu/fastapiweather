import httpx
from fastapi import FastAPI, Depends, HTTPException
from app.db.session import AsyncSessionLocal
from app.services.weather_service import fetch_weather
from app.repositories.weather_repository import get_or_create_city, save_weather

app = FastAPI()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.get("/weather")
async def get_weather(city: str, lat: float, lon: float, db=Depends(get_db)):
    # 1. Call external API (async)
    try:
        weather_response = await fetch_weather(lat, lon)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Weather provider returned {exc.response.status_code}",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Weather provider unavailable",
        ) from exc

    current = weather_response.get("current_weather")
    if not current:
        raise HTTPException(
            status_code=502,
            detail="Weather provider response missing current weather data",
        )

    temperature = current.get("temperature")
    if temperature is None:
        raise HTTPException(
            status_code=502,
            detail="Weather provider response missing temperature",
        )

    # 2. Store in DB
    city_obj = await get_or_create_city(db, city, "CR")

    await save_weather(
        db, city_obj.id, {"temperature": temperature, "relativehumidity": 50}
    )

    return {"city": city, "temperature": temperature}
