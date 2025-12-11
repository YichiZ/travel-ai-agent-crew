from app.models.model import FlightRequest, HotelRequest, AIResponse, ConversationRequest, ChatRequest, KeepChatRequest
import uvicorn
import asyncio
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from app.services.llm import LLMService
from app.services.crew import CrewAIService
from app.services.serp import SerpAPIService
from dotenv import load_dotenv
from crewai import Crew, Process
from app.services.chat import ChatService
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


@app.post("/search_flights/")
async def search_flights(
    flight_request: FlightRequest,
    serp_service: Annotated[SerpAPIService, Depends()]
):
    """Search for flights using SerpAPI."""
    return await serp_service.search_flights(flight_request)


@app.post("/search_hotels/")
async def search_hotels(
    hotel_request: HotelRequest,
    serp_service: Annotated[SerpAPIService, Depends()]
):
    """Search for hotels using SerpAPI."""
    return await serp_service.search_hotels(hotel_request)


@app.post("/generate_itinerary_from_conversation/", response_model=AIResponse)
async def get_itinerary_from_conversation(
    conversation_request: ConversationRequest,
    crew_service: Annotated[CrewAIService, Depends()],
    llm_service: Annotated[LLMService, Depends()]
):
    """Generate an itinerary based on provided conversation."""

    itinerary_json = llm_service.parse_itinerary(
        conversation_request.conversation_text)

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

    (flight_task, flight_agent) = await crew_service.create_flight_entities(
        flight_request)
    (hotel_task, hotel_agent) = await crew_service.create_hotel_entities(
        hotel_request)

    (recommendation_task, recommendation_agent) = await crew_service.create_recommendation_entities(flight_task, hotel_task)

    (itinerary_task, itinerary_agent) = await crew_service.generate_itinerary(flight_task, hotel_task, recommendation_task)

    crew = Crew(
        agents=[flight_agent, hotel_agent,
                recommendation_agent, itinerary_agent],
        tasks=[flight_task, hotel_task, recommendation_task, itinerary_task],
        process=Process.sequential,
        verbose=True,
    )

    crew_results = await asyncio.to_thread(crew.kickoff)
    itinerary = crew_results.raw

    return AIResponse(
        itinerary_json=itinerary_json,
        itinerary=itinerary
    )


@app.post("/start_chat/")
async def start_chat(
    chat_request: ChatRequest,
    chat_service: Annotated[ChatService, Depends()]
):
    """Start a new chat."""
    return chat_service.start_chat(chat_request)


@app.post("/keep_chat/")
async def keep_chat(
    keep_chat_request: KeepChatRequest,
    chat_service: Annotated[ChatService, Depends()]
):
    """Keep chatting with the chat assistant using the chat ID."""
    return chat_service.keep_chat(keep_chat_request)


if __name__ == "__main__":
    logger.info("Starting Travel Planning API server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
