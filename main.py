import uvicorn
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, Annotated
from models.model import FlightRequest, HotelRequest, ItineraryRequest, AIResponse, WorkflowType
from services.serp import SerpAPIService
from services.crew import CrewAIService
from dotenv import load_dotenv
from helpers.helper import format_travel_data
load_dotenv()

# Initialize Logger
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


app = FastAPI(title="Travel Planning API", version="1.1.0")


@app.post("/search_flights/", response_model=AIResponse)
async def get_flight_recommendations(
    flight_request: FlightRequest,
    serp_service: Annotated[SerpAPIService, Depends()],
    crew_service: Annotated[CrewAIService, Depends()]
):
    """Search flights and get AI recommendation."""
    try:
        flights = await serp_service.search_flights(flight_request)
        flights_text = format_travel_data("flights", flights)
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
        hotels_text = format_travel_data("hotels", hotels)
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
        flights_text = format_travel_data("flights", flights)
        hotels_text = format_travel_data("hotels", hotels)

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

if __name__ == "__main__":
    logger.info("Starting Travel Planning API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
