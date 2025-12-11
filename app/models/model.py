"""
Models module for the travel planner API.
Contains all Pydantic models for requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class WorkflowType(Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    TRAVEL = "travel"


class CreateTaskOptions(BaseModel):
    task_type: WorkflowType = Field(
        WorkflowType.FLIGHT, description="Type of workflow task")
    formatted_data: Optional[str] = Field(
        default=None, description="Formatted data for the task")
    destination: Optional[str] = Field(
        default=None, description="Travel destination")
    flights_text: Optional[str] = Field(
        default=None, description="Flight information text")
    hotels_text: Optional[str] = Field(
        default=None, description="Hotel information text")
    check_in_date: Optional[str] = Field(
        default=None, description="Check-in date in YYYY-MM-DD format")
    check_out_date: Optional[str] = Field(
        default=None, description="Check-out date in YYYY-MM-DD format")
    conversation_text: Optional[str] = Field(
        default=None, description="Free-form conversation text describing the travel request")


class FlightRequest(BaseModel):
    origin: str = Field(default="SFO", description="Origin airport IATA code")
    destination: str = Field(
        default="JFK", description="Destination airport IATA code")
    outbound_date: str = Field(
        default="2025-12-01", description="Outbound date in YYYY-MM-DD format")
    return_date: str = Field(default="2025-12-15",
                             description="Return date in YYYY-MM-DD format")
    conversation_text: str = Field(
        default="", description="Free-form conversation text describing the travel request")


class HotelRequest(BaseModel):
    location: str = Field(default="New York",
                          description="Hotel location or city name")
    check_in_date: str = Field(
        default="2025-12-01", description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(
        default="2025-12-15", description="Check-out date in YYYY-MM-DD format")
    conversation_text: str = Field(
        default="", description="Free-form conversation text describing the travel request")


class ItineraryRequest(BaseModel):
    destination: str
    check_in_date: str
    check_out_date: str
    flights: str
    hotels: str


class FlightInfo(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    departure: str
    arrival: str
    travel_class: str
    return_date: str
    airline_logo: str


class FlightInfoList(BaseModel):
    flights: List[FlightInfo]


class HotelInfo(BaseModel):
    name: str
    price: str
    rating: float
    location: str
    link: str
    check_in_date: str
    check_out_date: str


class HotelInfoList(BaseModel):
    hotels: List[HotelInfo]


class RecommendationInfo(BaseModel):
    selected_flight: FlightInfo
    selected_hotel: HotelInfo


class ItineraryResponse(BaseModel):
    departure_location: str
    departure_date: str
    arrival_location: str
    arrival_date: str
    departure_flight_airport_code: str
    arrival_flight_airport_code: str


class AIResponse(BaseModel):
    itinerary: str = ""
    itinerary_json: ItineraryResponse = Field(
        description="Structured itinerary data with location and date information"
    )


class ConversationRequest(BaseModel):
    conversation_text: str = Field(
        description="Free-form conversation text describing the travel request")


class ChatRequest(BaseModel):
    itinerary: str = Field(
        description="Detailed itinerary for the travel request")
    human_message: str = Field(
        description="Human message to send to the chat assistant")


class KeepChatRequest(BaseModel):
    chat_id: str = Field(
        description="Chat ID to keep the chat")
    human_message: str = Field(
        description="Human message to send to the chat assistant")


class ChatsHistory(BaseModel):
    """Model representing chat history with UUID as chat_id and list of LangChain messages."""
    chats_history: dict[str, List[Union[SystemMessage, HumanMessage, AIMessage]]] = Field(
        default_factory=dict,
        description="Dictionary mapping chat_id (UUID) to list of SystemMessage, HumanMessage, or AIMessage"
    )
