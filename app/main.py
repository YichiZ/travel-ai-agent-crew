from app.models.model import FlightRequest, HotelRequest, ItineraryRequest, AIResponse, WorkflowType, ItineraryResponse, ConversationRequest
import uvicorn
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Annotated
from app.services.serp import SerpAPIService
from app.services.crew import CrewAIService
from dotenv import load_dotenv
from app.helpers.helper import format_flight_data, format_hotel_data
load_dotenv()


# Initialize Logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI(title="Travel Planning API", version="1.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Common React dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://unprolix-qualmishly-emile.ngrok-free.dev",  # ngrok domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search_flights/", response_model=AIResponse)
async def get_flight_recommendations(
    flight_request: FlightRequest,
    serp_service: Annotated[SerpAPIService, Depends()],
    crew_service: Annotated[CrewAIService, Depends()]
):
    """Search flights and get AI recommendation."""
    try:
        flights = await serp_service.search_flights(flight_request)
        flights_text = format_flight_data(flights)
        ai_recommendation = await crew_service.get_ai_recommendation(WorkflowType.FLIGHT, flights_text)

        return AIResponse(
            flights=flights if isinstance(flights, list) else [],
            ai_flight_recommendation=ai_recommendation
        )
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.exception(f"Flight search endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Flight search error: {str(e)}")


@app.post("/search_hotels/", response_model=AIResponse)
async def get_hotel_recommendations(
    hotel_request: HotelRequest,
    serp_service: Annotated[SerpAPIService, Depends()],
    crew_service: Annotated[CrewAIService, Depends()]
):
    """Search hotels and get AI recommendation."""
    try:
        # Fetch hotel data
        hotels = await serp_service.search_hotels(hotel_request)
        hotels_text = format_hotel_data(hotels)
        ai_recommendation = await crew_service.get_ai_recommendation(WorkflowType.HOTEL, hotels_text)

        return AIResponse(
            hotels=hotels if isinstance(hotels, list) else [],
            ai_hotel_recommendation=ai_recommendation
        )
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status codes
        raise
    except Exception as e:
        logger.exception(f"Hotel search endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Hotel search error: {str(e)}")


@app.post("/complete_search/", response_model=AIResponse)
async def get_complete_travel_search(
    flight_request: FlightRequest,
    hotel_request: Optional[HotelRequest],
    serp_service: Annotated[SerpAPIService, Depends()],
    crew_service: Annotated[CrewAIService, Depends()]
):
    """Search for flights and hotels concurrently and get AI recommendations for both."""
    try:
        # If hotel request is not provided, create one from flight request
        if hotel_request is None:
            hotel_request = HotelRequest(
                location=flight_request.destination,
                check_in_date=flight_request.outbound_date,
                check_out_date=flight_request.return_date
            )

        # Run flight and hotel searches concurrently
        flight_task = asyncio.create_task(get_flight_recommendations(
            flight_request, serp_service, crew_service))
        hotel_task = asyncio.create_task(get_hotel_recommendations(
            hotel_request, serp_service, crew_service))

        # Wait for both tasks to complete
        flight_results, hotel_results = await asyncio.gather(flight_task, hotel_task, return_exceptions=True)

        # Initialize empty results
        flights = []
        hotels = []
        ai_flight_recommendation = "Could not retrieve flights."
        ai_hotel_recommendation = "Could not retrieve hotels."
        itinerary = ""

        # Process flight results if successful
        if isinstance(flight_results, AIResponse):
            flights = flight_results.flights
            ai_flight_recommendation = flight_results.ai_flight_recommendation

        # Process hotel results if successful
        if isinstance(hotel_results, AIResponse):
            hotels = hotel_results.hotels
            ai_hotel_recommendation = hotel_results.ai_hotel_recommendation

        # Format data for itinerary generation
        flights_text = format_flight_data(flights)
        hotels_text = format_hotel_data(hotels)

        # Generate itinerary if both searches were successful
        if flights and hotels:
            itinerary = await crew_service.generate_itinerary(
                destination=flight_request.destination,
                flights_text=flights_text,
                hotels_text=hotels_text,
                check_in_date=flight_request.outbound_date,
                check_out_date=flight_request.return_date
            )

        # Combine results
        return AIResponse(
            flights=flights,
            hotels=hotels,
            ai_flight_recommendation=ai_flight_recommendation,
            ai_hotel_recommendation=ai_hotel_recommendation,
            itinerary=itinerary
        )
    except Exception as e:
        logger.exception(f"Complete travel search error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Travel search error: {str(e)}")


@app.post("/generate_itinerary/", response_model=AIResponse)
async def get_itinerary(
    itinerary_request: ItineraryRequest,
    crew_service: Annotated[CrewAIService, Depends()]
):
    """Generate an itinerary based on provided flight and hotel information."""
    try:
        itinerary = await crew_service.generate_itinerary(
            destination=itinerary_request.destination,
            flights_text=itinerary_request.flights,
            hotels_text=itinerary_request.hotels,
            check_in_date=itinerary_request.check_in_date,
            check_out_date=itinerary_request.check_out_date
        )

        return AIResponse(itinerary=itinerary)
    except Exception as e:
        logger.exception(f"Itinerary generation error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Itinerary generation error: {str(e)}")


@app.post("/generate_itinerary_from_conversation/", response_model=AIResponse)
async def get_itinerary_from_conversation(
    conversation_request: ConversationRequest,
    crew_service: Annotated[CrewAIService, Depends()],
    serp_service: Annotated[SerpAPIService, Depends()]
):
    """Generate an itinerary based on provided conversation."""

    task = crew_service.create_itinerary_task(
        conversation_request.conversation_text)
    itinerary_json = await crew_service.run_itinerary_task(task)

    if itinerary_json is None:
        raise HTTPException(
            status_code=500, detail="Unable to generate itinerary")

    flight_request = FlightRequest(
        origin=itinerary_json.departure_flight_airport_code,
        destination=itinerary_json.arrival_flight_airport_code,
        outbound_date=itinerary_json.departure_date,
        return_date=itinerary_json.arrival_date
    )

    hotel_request = HotelRequest(
        location=itinerary_json.arrival_location,
        check_in_date=itinerary_json.departure_date,
        check_out_date=itinerary_json.arrival_date
    )

    flight_recommendation = await crew_service.generate_flight_recommendation(
        flight_request)
    hotel_recommendation = await crew_service.generate_hotel_recommendation(
        hotel_request)

    flight_task = asyncio.create_task(get_flight_recommendations(
        flight_request, serp_service, crew_service))
    hotel_task = asyncio.create_task(get_hotel_recommendations(
        hotel_request, serp_service, crew_service))

    # Wait for both tasks to complete
    flight_results, hotel_results = await asyncio.gather(flight_task, hotel_task, return_exceptions=True)

    # Initialize empty results
    flights = []
    hotels = []
    ai_flight_recommendation = "Could not retrieve flights."
    ai_hotel_recommendation = "Could not retrieve hotels."
    itinerary = ""

    # Process flight results if successful
    if isinstance(flight_results, AIResponse):
        flights = flight_results.flights
        ai_flight_recommendation = flight_results.ai_flight_recommendation

    # Process hotel results if successful
    if isinstance(hotel_results, AIResponse):
        hotels = hotel_results.hotels
        ai_hotel_recommendation = hotel_results.ai_hotel_recommendation

    # Format data for itinerary generation
    flights_text = format_flight_data(flights)
    hotels_text = format_hotel_data(hotels)

    # Generate itinerary if both searches were successful
    if flights and hotels:
        itinerary = await crew_service.generate_itinerary(
            destination=flight_request.destination,
            flights_text=flights_text,
            hotels_text=hotels_text,
            check_in_date=flight_request.outbound_date,
            check_out_date=flight_request.return_date
        )

    return AIResponse(
        flights=flights,
        hotels=hotels,
        ai_flight_recommendation=ai_flight_recommendation,
        ai_hotel_recommendation=ai_hotel_recommendation,
        itinerary=itinerary
    )


if __name__ == "__main__":
    logger.info("Starting Travel Planning API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
