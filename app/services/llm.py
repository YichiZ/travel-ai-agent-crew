from app.models.model import ItineraryResponse
from datetime import datetime
from crewai import LLM


class LLMService:

    def __init__(self):
        self.model = "gemini/gemini-2.5-flash"

    def parse_itinerary(self, conversation: str) -> ItineraryResponse:
        today = datetime.now().strftime("%Y-%m-%d")
        description = f"""
            We want to create an itinerary based on the conversation.
            The conversation is: {conversation}
            Today's date is {today}.

            The output JSON schema is:
            {ItineraryResponse.model_json_schema()}

            If the conversation does not provide enough information do the following:
            1. The default departure location is San Francisco.
            2. Pick a common destination from the conversation.
            3. Pick a departure date in 1 month from today's date.
            4. If not mentioned, pick a return date 1 week after the departure date.

            The output should be a JSON object with the following fields:
            - departure_location: The departure location.
            - departure_date: The departure date.
            - arrival_location: The arrival location.
            - arrival_date: The arrival date.
            - departure_flight_airport_code: The departure flight airport code closest to the departure location.
            - arrival_flight_airport_code: The arrival flight airport code closest to the arrival location.

            Do not return the json in markdown code blocks.
            """

        llm = LLM(model=self.model, response_format=ItineraryResponse)
        response = llm.call(messages=description)
        return ItineraryResponse.model_validate_json(response)
