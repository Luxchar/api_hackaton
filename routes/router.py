from typing import List
import uuid
from fastapi import APIRouter, Request, HTTPException, status
from bson.objectid import ObjectId
import math
from geopy.geocoders import Nominatim
from typing import List, Union, Dict
from pydantic import BaseModel

router = APIRouter()

@router.get("/ping")
async def ping(request: Request):
    """ Check if the API is running """
    return {"ping": "pong"}

async def get_coordinates(address: str) -> Dict[str, float]:
    """Convert address to coordinates"""
    geolocator = Nominatim(user_agent="carbon_footprint_calculator")
    location = geolocator.geocode(address)
    if location:
        return {"lat": location.latitude, "lng": location.longitude}
    raise ValueError(f"Could not geocode address: {address}")

class Coordinate(BaseModel):
    lat: float
    lng: float

class ItineraryRequest(BaseModel):
    itinerary: List[Union[Coordinate, str]]

@router.post("/footprint", response_description="Get Carbon Footprint of an Itinerary", status_code=status.HTTP_201_CREATED)
async def footprint(request: Request, body: ItineraryRequest):
    """Calculate the CO2 footprint of an itinerary"""
    
    footprints = {
        "carFootprint": 0.0,
        "busFootprint": 0.0,
        "truckFootprint": 0.0,
        "trainFootprint": 0.0,
        "planeFootprint": 0.0,
        "walkingFootprint": 0.0, 
        "bikingFootprint": 0.0
    }

    # Convert addresses to coordinates if needed
    coordinates = []
    for point in body.itinerary:
        if isinstance(point, str):
            coords = await get_coordinates(point)
            coordinates.append(coords)
        else:
            coordinates.append({"lat": point.lat, "lng": point.lng})

    # Calculate total distance from points
    total_distance = 0
    for i in range(len(coordinates)-1):
        start = coordinates[i]
        end = coordinates[i+1]
        
        # Calculate distance between points using Haversine formula
        R = 6371  # Earth's radius in km
        lat1, lon1 = start['lat'], start['lng']
        lat2, lon2 = end['lat'], end['lng']
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        total_distance += distance

    # Calculate footprints based on distance and emission factors
    footprints["carFootprint"] = total_distance * 120  # 120g CO2/km
    footprints["busFootprint"] = total_distance * 80   # 80g CO2/km
    footprints["truckFootprint"] = total_distance * 160  # 160g CO2/km
    footprints["trainFootprint"] = total_distance * 30   # 30g CO2/km
    footprints["planeFootprint"] = total_distance * 150  # 150g CO2/km
    footprints["walkingFootprint"] = total_distance * 10  # 10g CO2/km
    footprints["bikingFootprint"] = total_distance * 10   # 10g CO2/km

    return footprints
