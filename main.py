from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

GOOGLE_PLACES_API_KEY = "Teruel 7090"

# curl -X POST "http://0.0.0.0:8000/nearby_veterinaries/" -H "Content-Type: application/json" -d '{"latitude": X, "longitude": Y}'

class Location(BaseModel):
    latitude: float
    longitude: float

# Returns alexa model
@app.get("/")
def get_model():
    return "Alexa"

# Returns nearby veterinaries in a given location
@app.post("/nearby_veterinaries/")
def get_nearby_veterinaries(location: Location):
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={location.latitude},{location.longitude}"
        f"&radius=5000&type=veterinary_care&key={GOOGLE_PLACES_API_KEY}"
    )
    response = requests.get(places_url)
    places_data = response.json()

    if 'results' in places_data and places_data['results']:
        veterinaries = [
            {
                "name": place["name"],
                "address": place["vicinity"]
            }
            for place in places_data["results"]
        ]
        return {"veterinaries": veterinaries}
    else:
        raise HTTPException(status_code=404, detail="No veterinary clinics found nearby")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)