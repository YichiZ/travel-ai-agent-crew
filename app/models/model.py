"""
Models module for the travel planner API.
Contains all Pydantic models for requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


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


class FlightRequest(BaseModel):
    origin: str = Field(default="SFO", description="Origin airport IATA code")
    destination: str = Field(
        default="JFK", description="Destination airport IATA code")
    outbound_date: str = Field(
        default="2025-12-01", description="Outbound date in YYYY-MM-DD format")
    return_date: str = Field(default="2025-12-15",
                             description="Return date in YYYY-MM-DD format")


class HotelRequest(BaseModel):
    location: str = Field(default="New York",
                          description="Hotel location or city name")
    check_in_date: str = Field(
        default="2025-12-01", description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(
        default="2025-12-15", description="Check-out date in YYYY-MM-DD format")


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


class HotelInfo(BaseModel):
    name: str
    price: str
    rating: float
    location: str
    link: str


class AIResponse(BaseModel):
    flights: List[FlightInfo] = []
    hotels: List[HotelInfo] = []
    ai_flight_recommendation: str = ""
    ai_hotel_recommendation: str = ""
    itinerary: str = ""
