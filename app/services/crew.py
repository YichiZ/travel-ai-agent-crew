import logging
from crewai import Agent, Task
from app.models.model import WorkflowType, FlightRequest, FlightInfoList, HotelInfoList, HotelRequest
from crewai_tools import RagTool, SerpApiGoogleSearchTool
import os

logger = logging.getLogger(__name__)


class CrewAIService:
    """Service for handling AI recommendations and itinerary generation using CrewAI."""

    def __init__(self):
        self.llm_model = "gemini/gemini-2.5-flash"
        self.api_key = os.getenv("SERP_API_KEY")

    async def create_flight_entities(self, flight_request: FlightRequest) -> tuple[Task, Agent]:
        """Generate a flight recommendation based on the flight request."""
        search_query_object = {
            "engine": "google_flights",
            "hl": "en",
            "gl": "us",
            "departure_id": flight_request.origin.strip().upper(),
            "arrival_id": flight_request.destination.strip().upper(),
            "outbound_date": flight_request.outbound_date,
            "return_date": flight_request.return_date,
            "currency": "USD"
        }

        flight_search_tool = SerpApiGoogleSearchTool(
            search_query=str(search_query_object))

        agent = Agent(
            role="AI Flight Analyst",
            goal=("Analyze flight options and recommend the best one considering price, "
                  "duration, stops, and overall convenience."),
            backstory=("AI expert that provides in-depth analysis comparing flight options "
                       "based on multiple factors."),
            llm=self.llm_model,
            verbose=False,
            tools=[flight_search_tool],
        )

        task = Task(
            description=f"""
            We want to generate a flight recommendation based on the flight request. Limit the search to 5 results.
            The flight request is: {flight_request.model_dump_json()}

            You can use the flight_search_tool to get flight options.

            Output should be a FlightInfoList object.
            {FlightInfoList.model_json_schema()}

            flights: a list of FlightInfo objects.

            FlightInfo object should have the following fields:
            - airline: The airline name.
            - price: The price of the flight.
            - duration: The duration of the flight.
            - stops: The number of stops on the flight.
            - departure: The departure airport.
            - arrival: The arrival airport.
            - travel_class: The travel class of the flight.
            - return_date: The return date of the flight.
            - airline_logo: The logo of the airline.

            """,
            agent=agent,
            expected_output="A structured itinerary response based on the conversation.",
            output_pydantic=FlightInfoList,
            async_execution=True
        )
        return task, agent

    async def create_hotel_entities(self, hotel_request: HotelRequest) -> tuple[Task, Agent]:
        """Generate a hotel recommendation based on the hotel request."""
        search_query_object = {
            "engine": "google_hotels",
            "q": hotel_request.location,
            "hl": "en",
            "gl": "us",
            "check_in_date": hotel_request.check_in_date,
            "check_out_date": hotel_request.check_out_date,
            "currency": "USD",
            "sort_by": 3,
            "rating": 8
        }

        hotel_search_tool = SerpApiGoogleSearchTool(
            search_query=str(search_query_object)
        )

        agent = Agent(
            role="AI Hotel Analyst",
            goal=("Analyze hotel options and recommend the best one considering price, "
                  "rating, location, and amenities."),
            backstory=("AI expert that provides in-depth analysis comparing hotel options "
                       "based on multiple factors."),
            llm=self.llm_model,
            verbose=False,
            tools=[hotel_search_tool],
        )

        task = Task(
            description=f"""
            We want to generate a hotel recommendation based on the hotel request. Limit the search to 8 results.
            The hotel request is: {hotel_request.model_dump_json()}

            You can use the hotel_search_tool to get hotel options.

            The output should be a JSON object with the following fields:
            hotels: a list of HotelInfo objects.

            HotelInfo object should have the following fields:
            - name: The name of the hotel.
            - price: The price of the hotel.
            - rating: The rating of the hotel.
            - location: The location of the hotel.
            - link: The link to the hotel.
            - check_in_date: The check-in date of the hotel.
            - check_out_date: The check-out date of the hotel.

            The output should be a valid JSON object.
            """,
            agent=agent,
            expected_output="A structured hotel recommendation response based on the hotel request.",
            output_pydantic=HotelInfoList,
            async_execution=True
        )

        return task, agent

    async def generate_itinerary(self, flight_task: Task, hotel_task: Task) -> tuple[Task, Agent]:
        """Generate an itinerary based on the conversation text."""
        travel_tips_tool = RagTool()

        travel_tips_tool.add(
            data_type="website", url="https://www.nomadicmatt.com/travel-blogs/61-travel-tips/"
        )

        agent = Agent(
            role="AI Travel Planner",
            goal="Create a detailed itinerary for the user based on flight and hotel information and travel tips. Use the travel tips to help create a detailed itinerary.",
            backstory=("AI travel expert generating a day-by-day itinerary including flight "
                       "details, hotel stays, and must-visit locations in the destination."),
            llm=self.llm_model,
            verbose=False,
            tools=[travel_tips_tool],
        )

        task = Task(
            description=f"""
            We want to generate an itinerary based on the flight and hotel information.

            The itinerary should include:
            - Summary of the dates, flights and hotels.
            - Flight arrival and departure information
            - Hotel check-in and check-out details
            - Day-by-day breakdown of activities
            - Must-visit attractions and estimated visit times
            - Restaurant recommendations for meals
            - Tips for local transportation

            📝 **Format Requirements**:
            - Use markdown formatting with clear headings (# for main headings, ## for days, ### for sections)
            - Include emojis for different types of activities (🏛️ for landmarks, 🍽️ for restaurants, etc.)
            - Use bullet points for listing activities
            - Include estimated timings for each activity
            - Format the itinerary to be visually appealing and easy to read
            """,
            agent=agent,
            context=[flight_task, hotel_task],
            expected_output="A detailed itinerary of the city based on the flight and hotel information.",
        )

        return task, agent

    def get_recommendation_prompt(self, workflow_type: WorkflowType) -> str | None:
        """Create a task description based on the workflow type."""
        match workflow_type:
            case WorkflowType.FLIGHT:
                return """
                Recommend the best flight from the available options, based on the details provided below:

                **Reasoning for Recommendation:**
                - **💰 Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
                - **⏱️ Duration:** Explain why this flight has the best duration in comparison to others.
                - **🛑 Stops:** Discuss why this flight has minimal or optimal stops.
                - **💺 Travel Class:** Describe why this flight provides the best comfort and amenities.

                Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
                """
            case WorkflowType.HOTEL:
                return """
                    Based on the following analysis, generate a detailed recommendation for the best hotel. Your response should include clear reasoning based on price, rating, location, and amenities.

                    **🏆 AI Hotel Recommendation**
                    We recommend the best hotel based on the following analysis:

                    **Reasoning for Recommendation**:
                    - **💰 Price:** The recommended hotel is the best option for the price compared to others, offering the best value for the amenities and services provided.
                    - **⭐ Rating:** With a higher rating compared to the alternatives, it ensures a better overall guest experience. Explain why this makes it the best choice.
                    - **📍 Location:** The hotel is in a prime location, close to important attractions, making it convenient for travelers.
                    - **🛋️ Amenities:** The hotel offers amenities like Wi-Fi, pool, fitness center, free breakfast, etc. Discuss how these amenities enhance the experience, making it suitable for different types of travelers.

                    📝 **Reasoning Requirements**:
                    - Ensure that each section clearly explains why this hotel is the best option based on the factors of price, rating, location, and amenities.
                    - Compare it against the other options and explain why this one stands out.
                    - Provide concise, well-structured reasoning to make the recommendation clear to the traveler.
                    - Your recommendation should help a traveler make an informed decision based on multiple factors, not just one.
                    """
            case _:
                raise ValueError(f"Unsupported workflow type: {workflow_type}")
