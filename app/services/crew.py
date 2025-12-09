import asyncio
import logging
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from app.models.model import WorkflowType, CreateTaskOptions, ItineraryResponse, FlightRequest, FlightInfo, FlightInfoList, HotelInfo, HotelInfoList, HotelRequest
from crewai_tools import RagTool, SerpApiGoogleSearchTool
import os

from typing import List

logger = logging.getLogger(__name__)


class CrewAIService:
    """Service for handling AI recommendations and itinerary generation using CrewAI."""

    def __init__(self):
        self.travel_agent = self.__create_agent(WorkflowType.TRAVEL)
        self.hotel_agent = self.__create_agent(WorkflowType.HOTEL)
        self.flight_agent = self.__create_agent(WorkflowType.FLIGHT)

        self.api_key = os.getenv("SERP_API_KEY")

    async def generate_flight_recommendation(self, flight_request: FlightRequest) -> FlightInfoList:
        """Generate a flight recommendation based on the flight request."""
        llm_model = "gemini/gemini-2.5-flash"

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
            role="AI Flight Recommendation Agent. Tools: Use the serp api to get flight options. Input: Hotel request.",
            goal=("Analyze flight options and recommend the best one considering price, "
                  "duration, stops, and overall convenience."),
            backstory=("AI expert that provides in-depth analysis comparing flight options "
                       "based on multiple factors."),
            llm=llm_model,
            verbose=False,
            tools=[flight_search_tool]
        )

        task = Task(
            description=f"""
            We want to generate a flight recommendation based on the flight request.
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
            output_pydantic=FlightInfoList
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        crew_results = await asyncio.to_thread(crew.kickoff)
        return crew_results.pydantic

    async def generate_hotel_recommendation(self, hotel_request: HotelRequest) -> HotelInfoList:
        """Generate a hotel recommendation based on the hotel request."""
        llm_model = "gemini/gemini-2.5-flash"

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
            role="AI Hotel Recommendation Agent. Tools: Use the serp api to get hotel options. Input: Hotel request.",
            goal=("Analyze hotel options and recommend the best one considering price, "
                  "rating, location, and amenities."),
            backstory=("AI expert that provides in-depth analysis comparing hotel options "
                       "based on multiple factors."),
            llm=llm_model,
            verbose=False,
            tools=[hotel_search_tool]
        )

        task = Task(
            description=f"""
            We want to generate a hotel recommendation based on the hotel request.
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

            The output should be a valid JSON object.
            """,
            agent=agent,
            expected_output="A structured hotel recommendation response based on the hotel request.",
            output_pydantic=HotelInfoList
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        crew_results = await asyncio.to_thread(crew.kickoff)
        return crew_results.pydantic

    async def get_ai_recommendation(self, data_type: WorkflowType, formatted_data: str, conversation_text: str) -> str:
        """Unified function for getting AI recommendations for both flights and hotels."""
        logger.info(f"Getting {data_type} analysis from AI")

        options = CreateTaskOptions(
            task_type=WorkflowType(data_type),
            formatted_data=formatted_data,
            conversation_text=conversation_text
        )

        analyst_crew = self.__create_crew(data_type, options)
        try:
            # Run the CrewAI analysis in a thread pool
            crew_results = await asyncio.to_thread(analyst_crew.kickoff)

            # Handle different possible return types from CrewAI
            if hasattr(crew_results, 'raw'):
                return crew_results.raw
            else:
                return str(crew_results)
        except Exception as e:
            logger.exception(f"Error in AI {data_type} analysis: {str(e)}")
            return f"Unable to generate {data_type} recommendation due to an error."

    async def generate_itinerary(self, destination: str, flights_text: str, hotels_text: str, check_in_date: str, check_out_date: str) -> str:
        """Generate a detailed travel itinerary based on flight and hotel information."""
        try:
            options = CreateTaskOptions(
                task_type=WorkflowType.TRAVEL,
                destination=destination,
                flights_text=flights_text,
                hotels_text=hotels_text,
                check_in_date=check_in_date,
                check_out_date=check_out_date
            )

            crew = self.__create_crew(WorkflowType.TRAVEL, options)

            crew_results = await asyncio.to_thread(crew.kickoff)

            # Handle different possible return types from CrewAI
            if hasattr(crew_results, 'raw'):
                return crew_results.raw
            else:
                return str(crew_results)
        except Exception as e:
            logger.exception(f"Error generating itinerary: {str(e)}")
            return "Unable to generate itinerary due to an error. Please try again later."

    def create_itinerary_task(self, conversation: str) -> Task:
        """Create a task to parse the itinerary from the conversation."""
        llm_model = "gemini/gemini-2.5-flash"

        today = datetime.now().strftime("%Y-%m-%d")

        return Task(
            description=f"""
            We want to create an itinerary based on the conversation.
            The conversation is: {conversation}
            Today's date is {today}.

            The output JSON schema is:
            {ItineraryResponse.model_json_schema()}

            If the conversation does not provide enough information do the following:
            1. The default departure location is San Francisco.
            1. Pick a common destination from the conversation.
            2. Pick a departure date in 1 month from today's date.
            3. Pick a return date a week after the departure date.

            The output should be a JSON object with the following fields:
            - departure_location: The departure location.
            - departure_date: The departure date.
            - arrival_location: The arrival location.
            - arrival_date: The arrival date.
            - departure_flight_airport_code: The departure flight airport code closest to the departure location.
            - arrival_flight_airport_code: The arrival flight airport code closest to the arrival location.

            The output should be a valid JSON object.
            """,
            agent=self.travel_agent,
            expected_output="A structured itinerary response based on the conversation.",
            output_pydantic=ItineraryResponse
        )

    async def run_itinerary_task(self, task: Task) -> ItineraryResponse | None:
        """Run the itinerary task and return the result."""

        agent = self.__get_agent(WorkflowType.TRAVEL)

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False,
        )
        crew_results = await asyncio.to_thread(crew.kickoff)
        try:
            itinerary_response = ItineraryResponse.model_validate(
                crew_results.pydantic)
            return itinerary_response
        except Exception as e:
            logger.exception(f"Error parsing itinerary: {str(e)}")
            return None

    # region Private helper methods
    def __get_agent(self, agent_type: WorkflowType) -> Agent:
        """Retrieve the appropriate agent based on the workflow type."""
        match agent_type:
            case WorkflowType.FLIGHT:
                return self.flight_agent
            case WorkflowType.HOTEL:
                return self.hotel_agent
            case WorkflowType.TRAVEL:
                return self.travel_agent

    def __create_agent(self, agent_type: WorkflowType) -> Agent:
        """Create an agent for the given workflow type."""
        # Default LLM model for the service
        llm_model = "gemini/gemini-2.5-flash"

        match agent_type:
            case WorkflowType.FLIGHT:
                return Agent(
                    role="AI Flight Analyst",
                    goal=("Analyze flight options and recommend the best one considering price, "
                          "duration, stops, and overall convenience."),
                    backstory=("AI expert that provides in-depth analysis comparing flight options "
                               "based on multiple factors."),
                    llm=llm_model,
                    verbose=False,
                )
            case WorkflowType.HOTEL:
                return Agent(
                    role="AI Hotel Analyst",
                    goal=("Analyze hotel options and recommend the best one considering price, "
                          "rating, location, and amenities."),
                    backstory=("AI expert that provides in-depth analysis comparing hotel options "
                               "based on multiple factors."),
                    llm=llm_model,
                    verbose=False,
                )
            case WorkflowType.TRAVEL:
                return Agent(
                    role="AI Travel Planner",
                    goal="Create a detailed itinerary for the user based on flight and hotel information",
                    backstory=("AI travel expert generating a day-by-day itinerary including flight "
                               "details, hotel stays, and must-visit locations in the destination."),
                    llm=llm_model,
                    verbose=False,
                )

    def __create_task(self, agent, options: CreateTaskOptions) -> Task:
        """Create a task based on the provided options."""
        description = ""

        match options.task_type:
            case WorkflowType.FLIGHT:
                description = """
                Recommend the best flight from the available options, based on the details provided below:

                **Reasoning for Recommendation:**
                - **💰 Price:** Provide a detailed explanation about why this flight offers the best value compared to others.
                - **⏱️ Duration:** Explain why this flight has the best duration in comparison to others.
                - **🛑 Stops:** Discuss why this flight has minimal or optimal stops.
                - **💺 Travel Class:** Describe why this flight provides the best comfort and amenities.

                Use the provided flight data as the basis for your recommendation. Be sure to justify your choice using clear reasoning for each attribute. Do not repeat the flight details in your response.
                """
            case WorkflowType.HOTEL:
                description = """
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
            case WorkflowType.TRAVEL:
                if not options.destination or not options.flights_text or not options.check_in_date or not options.check_out_date:
                    raise ValueError(
                        "Destination, flight information, check_in_date or check_out_date must be provided for travel itinerary tasks.")

                # Convert the string dates to datetime objects
                check_in = datetime.strptime(options.check_in_date, "%Y-%m-%d")
                check_out = datetime.strptime(
                    options.check_out_date, "%Y-%m-%d")

                # Calculate the difference in days
                days = (check_out - check_in).days

                description = f"""
                    Based on the following details, create a {days}-day itinerary for the user:

                    **Flight Details**:
                    {options.flights_text}

                    **Hotel Details**:
                    {options.hotels_text}

                    **Destination**: {options.destination}

                    **Travel Dates**: {options.check_in_date} to {options.check_out_date} ({days} days)

                    The itinerary should include:
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
                    """

        return Task(
            description=f"{description}\n\nData to analyze:\n{options.formatted_data}",
            agent=agent,
            expected_output=f"A structured recommendation explaining the best {options.task_type.value} choice based on the analysis of provided details."
        )

    def __get_blogger_agent(self) -> Agent:
        """Get the travel tips tool."""
        llm_model = "gemini/gemini-2.5-flash"

        rag_tool = RagTool(
        )

        rag_tool.add(
            data_type="website", url="https://www.nomadicmatt.com/travel-blogs/61-travel-tips/"
        )

        return Agent(
            role="Travel Blogger",
            goal="Create a travel blog post based on the itinerary provided",
            backstory="A travel blogger who creates engaging and informative blog posts about the destinations and experiences.",
            llm=llm_model,
            verbose=False,
            tools=[rag_tool],
        )

    def __create_crew(self, workflow_type: WorkflowType, options: CreateTaskOptions) -> Crew:
        """Create a crew for the given workflow type."""
        agent = self.__get_agent(workflow_type)
        task = self.__create_task(agent, options)

        agents = [agent]

        if workflow_type == WorkflowType.TRAVEL:
            agents.append(self.__get_blogger_agent())

        return Crew(
            # Ensure correct type for Crew constructor (list[BaseAgent])
            agents=list(agents),
            tasks=[task],
            process=Process.sequential,
            verbose=False,
            memory=True
        )
