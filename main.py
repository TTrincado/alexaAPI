from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import requests
# from decouple import config // no quizo funcionar e.e
import os

app = FastAPI()

GOOGLE_PLACES_API_KEY = os.getenv("API_KEY")

class Address(BaseModel):
    address: str

# Returns alexa model
@app.get("/")
def get_model():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Alexa API Model</title>
        <style>
            body {
                background-color: black;
                color: white;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div>
            <h1>Alexa API model code MiniDev-P01</h1>
            <p>OpenVet by MiniDev</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

def get_coordinates(address):
    geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(geocoding_url)
    geocoding_data = response.json()

    if 'results' in geocoding_data and geocoding_data['results']:
        location = geocoding_data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise HTTPException(status_code=404, detail="Address not found")

# Returns nearby veterinaries in a given address
@app.post("/nearby_veterinaries/")
def get_nearby_veterinaries(address: Address):
    latitude, longitude = get_coordinates(address.address)
    places_url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={latitude},{longitude}"
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