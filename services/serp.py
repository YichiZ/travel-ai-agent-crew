import asyncio
import logging
from fastapi import HTTPException
from serpapi import GoogleSearch
from typing import Dict, List, Any, Union
from models.model import FlightRequest, FlightInfo, HotelRequest, HotelInfo
import os

logger = logging.getLogger(__name__)


class SerpAPIService:
    def __init__(self):
        self.api_key = os.getenv("SERP_API_KEY")

    async def run_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generic function to run SerpAPI searches asynchronously."""
        try:
            return await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
        except Exception as e:
            logger.exception(f"SerpAPI search error: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Search API error: {str(e)}")

    async def search_flights(self, flight_request: FlightRequest) -> Union[List[FlightInfo], Dict[str, str]]:
        """Fetch real-time flight details from Google Flights using SerpAPI."""
        logger.info(
            f"Searching flights: {flight_request.origin} to {flight_request.destination}")

        search_results = await self.run_search({
            "api_key": self.api_key,
            "engine": "google_flights",
            "hl": "en",
            "gl": "us",
            "departure_id": flight_request.origin.strip().upper(),
            "arrival_id": flight_request.destination.strip().upper(),
            "outbound_date": flight_request.outbound_date,
            "return_date": flight_request.return_date,
            "currency": "USD"
        })

        if "error" in search_results:
            logger.error(f"Flight search error: {search_results['error']}")
            return {"error": search_results["error"]}

        best_flights = search_results.get("best_flights", [])
        if not best_flights:
            logger.warning("No flights found in search results")
            return []

        formatted_flights = []
        for flight in best_flights:
            if not flight.get("flights") or len(flight["flights"]) == 0:
                continue

            first_leg = flight["flights"][0]
            formatted_flights.append(FlightInfo(
                airline=first_leg.get("airline", "Unknown Airline"),
                price=str(flight.get("price", "N/A")),
                duration=f"{flight.get('total_duration', 'N/A')} min",
                stops="Nonstop" if len(
                    flight["flights"]) == 1 else f"{len(flight['flights']) - 1} stop(s)",
                departure=f"{first_leg.get('departure_airport', {}).get('name', 'Unknown')} ({first_leg.get('departure_airport', {}).get('id', '???')}) at {first_leg.get('departure_airport', {}).get('time', 'N/A')}",
                arrival=f"{first_leg.get('arrival_airport', {}).get('name', 'Unknown')} ({first_leg.get('arrival_airport', {}).get('id', '???')}) at {first_leg.get('arrival_airport', {}).get('time', 'N/A')}",
                travel_class=first_leg.get("travel_class", "Economy"),
                return_date=flight_request.return_date,
                airline_logo=first_leg.get("airline_logo", "")
            ))

        logger.info(f"Found {len(formatted_flights)} flights")
        return formatted_flights

    async def search_hotels(self, hotel_request: HotelRequest) -> Union[List[HotelInfo], Dict[str, str]]:
        """Fetch hotel information from SerpAPI."""
        logger.info(f"Searching hotels for: {hotel_request.location}")

        search_results = await self.run_search({
            "api_key": self.api_key,
            "engine": "google_hotels",
            "q": hotel_request.location,
            "hl": "en",
            "gl": "us",
            "check_in_date": hotel_request.check_in_date,
            "check_out_date": hotel_request.check_out_date,
            "currency": "USD",
            "sort_by": 3,
            "rating": 8
        })

        if "error" in search_results:
            logger.error(f"Hotel search error: {search_results['error']}")
            return {"error": search_results["error"]}

        hotel_properties = search_results.get("properties", [])
        if not hotel_properties:
            logger.warning("No hotels found in search results")
            return []

        formatted_hotels = []
        for hotel in hotel_properties:
            try:
                formatted_hotels.append(HotelInfo(
                    name=hotel.get("name", "Unknown Hotel"),
                    price=hotel.get("rate_per_night", {}).get("lowest", "N/A"),
                    rating=hotel.get("overall_rating", 0.0),
                    location=hotel.get("location", "N/A"),
                    link=hotel.get("link", "N/A")
                ))
            except Exception as e:
                logger.warning(f"Error formatting hotel data: {str(e)}")
                # Continue with next hotel rather than failing completely

        logger.info(f"Found {len(formatted_hotels)} hotels")
        return formatted_hotels
