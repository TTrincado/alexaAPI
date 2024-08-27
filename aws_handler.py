import logging
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from ask_sdk_model import Response


# OJO todo esto es codigo de chatgpt, aca ya no cacho muy bien la interaccion quiero esperar a que tengamos acceso
# a la consola de alexa para ver como se hace la interaccion

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FASTAPI_URL = "http://your-fastapi-server-url/nearby_veterinaries/"

class FindVeterinaryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("FindVeterinaryIntent")(handler_input)

    def handle(self, handler_input):
        # Get the user's location from the device settings
        device_id = handler_input.request_envelope.context.system.device.device_id
        api_access_token = handler_input.request_envelope.context.system.api_access_token
        api_endpoint = handler_input.request_envelope.context.system.api_endpoint

        headers = {
            'Authorization': f'Bearer {api_access_token}'
        }

        device_location_url = f'{api_endpoint}/v1/devices/{device_id}/settings/address/countryAndPostalCode'
        response = requests.get(device_location_url, headers=headers)
        location_data = response.json()

        if 'postalCode' in location_data:
            postal_code = location_data['postalCode']
            country_code = location_data['countryCode']

            # Call the FastAPI endpoint
            fastapi_response = requests.post(
                FASTAPI_URL,
                json={"latitude": location_data['latitude'], "longitude": location_data['longitude']}
            )
            fastapi_data = fastapi_response.json()

            if 'veterinaries' in fastapi_data:
                veterinary_name = fastapi_data['veterinaries'][0]['name']
                veterinary_address = fastapi_data['veterinaries'][0]['address']
                speech_text = f"The nearest veterinary clinic is {veterinary_name} located at {veterinary_address}."
            else:
                speech_text = "I couldn't find any veterinary clinics nearby."
        else:
            speech_text = "I couldn't retrieve your location. Please check your device settings."

        return handler_input.response_builder.speak(speech_text).set_should_end_session(True).response

sb = SkillBuilder()
sb.add_request_handler(FindVeterinaryIntentHandler())

lambda_handler = sb.lambda_handler()