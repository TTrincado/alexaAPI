from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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
    str_ = {
  "version": "1.0",
  "sessionAttributes": {},
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "Aquí tienes la veterinaria más cercana."
    },
    "card": {
      "type": "Simple",
      "title": "Veterinaria Cercana",
      "content": "La veterinaria más cercana está a 1.5 kilómetros de tu ubicación."
    },
    "reprompt": {
      "outputSpeech": {
        "type": "PlainText",
        "text": "¿Quieres encontrar otra veterinaria cercana?"
      }
    },
    "shouldEndSession": False
  }
}
    return JSONResponse(content=str_)

# Returns alexa model
@app.post("/")
def get_model():
    str_ = {
  "version": "1.0",
  "sessionAttributes": {},
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "Aquí tienes la veterinaria más cercana."
    },
    "card": {
      "type": "Simple",
      "title": "Veterinaria Cercana",
      "content": "La veterinaria más cercana está a 1.5 kilómetros de tu ubicación."
    },
    "reprompt": {
      "outputSpeech": {
        "type": "PlainText",
        "text": "¿Quieres encontrar otra veterinaria cercana?"
      }
    },
    "shouldEndSession": False
  }
}
    return JSONResponse(content=str_)


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

    try: 
        latitude, longitude = get_coordinates(address.address)
    except HTTPException as e:
        raise e
    
    places_url = (
        f"{API_URL}place/nearbysearch/json"
        f"?location={latitude},{longitude}"
        f"&rankby=distance&type=veterinary_care&key={GOOGLE_PLACES_API_KEY}"
        f"&opennow=true"
    )
    response = requests.get(places_url)
    places_data = response.json()

    if "results" in places_data and places_data["results"]:
        return {"nearest_veterinary": obtain_veterinaries(places_data)}
    else:
        raise HTTPException(
            status_code=404, detail="No veterinary clinics open found nearby"
        )

def get_coordinates(address):
    try:
        geocoding_url = (
            f"{API_URL}geocode/json?address={address}&key={GOOGLE_PLACES_API_KEY}"
        )
        response: Response = requests.get(geocoding_url)
        geocoding_data: dict = response.json()
        print(geocoding_data)

        if "results" in geocoding_data and geocoding_data["results"]:
            location = geocoding_data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            raise HTTPException(status_code=404, detail="Address not found")
    except Exception as e:
        raise e


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
