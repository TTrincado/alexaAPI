from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os


app = FastAPI(
    title="OpenVet",
    version="1.0.0",
    summary="OpenVet API, made for easy access to vets near you",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O puedes especificar ["https://alexa.amazon.com"] si deseas restringirlo
    allow_credentials=True,
    allow_methods=["*"],  # Puedes restringir a ["POST"] si solo usas POST
    allow_headers=["*"],
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

@app.post("/")
async def alexa_handler(request: Request):
    alexa_request = await request.json()
    
    # Cuando el usuario abre la skill
    if alexa_request["request"]["type"] == "LaunchRequest":
        return JSONResponse(content={
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Bienvenido a OpenVet. ¿En qué puedo ayudarte?"
                },
                "shouldEndSession": False
            }
        })

    elif alexa_request["request"]["type"] == "IntentRequest":
        intent_name = alexa_request["request"]["intent"]["name"]

        if intent_name == "GetNearbyVeterinaries":
            return JSONResponse(content={
                "version": "1.0",
                "response": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": "Buscando las veterinarias más cercanas..."
                    },
                    "shouldEndSession": False
                }
            })

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
