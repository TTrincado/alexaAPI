from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, Response
import requests


# from decouple import config // no quizo funcionar e.e
import os

app = FastAPI(
    title="OpenVet",
    version="1.0.0",
    summary="OpenVet API, made for easy access to vets near you",
)

GOOGLE_PLACES_API_KEY = os.getenv("API_KEY")

API_URL = "https://maps.googleapis.com/maps/api/"

tags_metadata = [
    {
        "name": "OpenVet",
        "description": "OpenVet API, made for easy access to vets near you",
    }
]


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


@app.post("/nearby_veterinaries/", tags=["OpenVet"])
def get_nearby_veterinaries(address: Address):
    latitude, longitude = get_coordinates(address.address)
    places_url = (
        f"{API_URL}place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&radius=5000&type=veterinary_care&key={GOOGLE_PLACES_API_KEY}"
    )
    response = requests.get(places_url)
    places_data = response.json()

    if "results" in places_data and places_data["results"]:
        return {
            "veterinaries": obtain_veterinaries(
                places_data, len(places_data["results"])
            )
        }
    else:
        raise HTTPException(
            status_code=404, detail="No veterinary clinics found nearby"
        )


@app.post("/nearest_veterinary/", tags=["OpenVet"])
def get_nearest_veterinary(address: Address):
    latitude, longitude = get_coordinates(address.address)
    places_url = (
        f"{API_URL}place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&rankby=distance&type=veterinary_care&key={GOOGLE_PLACES_API_KEY}"
    )
    response = requests.get(places_url)
    places_data = response.json()

    if "results" in places_data and places_data["results"]:
        return {"nearest_veterinary": obtain_veterinaries(places_data, 1)}
    else:
        raise HTTPException(
            status_code=404, detail="No veterinary clinics found nearby"
        )


@app.post("/nearest_open_veterinaries/", tags=["OpenVet"])
def get_nearest_open_veterinaries(address: Address):
    latitude, longitude = get_coordinates(address.address)
    places_url = (
        f"{API_URL}place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&rankby=distance&type=veterinary_care&key={GOOGLE_PLACES_API_KEY}"
        f"&opennow=true"
    )
    try:
        response = requests.get(places_url)
        places_data = response.json()

        if "results" in places_data and places_data["results"]:
            return {"nearest_veterinary": obtain_veterinaries(places_data)}
        else:
            raise HTTPException(
                status_code=404, detail="No veterinary clinics open found nearby"
            )
        
    except HTTPException as e:
        raise e


def get_coordinates(address):
    geocoding_url = (
        f"{API_URL}geocode/json?address={address}&key={GOOGLE_PLACES_API_KEY}"
    )
    response: Response = requests.get(geocoding_url)
    geocoding_data: dict = response.json()

    if "results" in geocoding_data and geocoding_data["results"]:
        location = geocoding_data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        raise HTTPException(status_code=404, detail="Address not found")


def obtain_veterinaries(response: Response, pagination_len: int = 3):
    veterinaries = []
    for i in range(
        pagination_len
        if len(response["results"]) > pagination_len
        else len(response["results"])
    ):
        veterinary = {
            "name": response["results"][i]["name"],
            "address": response["results"][i]["vicinity"],
        }
        veterinaries.append(veterinary)
    return veterinaries


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
