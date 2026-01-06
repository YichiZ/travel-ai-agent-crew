import os
import logging
import uuid
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import serpapi

from agents import Agent, Runner, function_tool, SQLiteSession
from app.models.model import FlightRequest, HotelRequest


logger = logging.getLogger(__name__)


load_dotenv()

router = APIRouter(
    prefix="/openai",
    tags=["openai"]
)


class GenerateTripRequest(BaseModel):
    """Request model for trip generation."""

    prompt: str
    sessionId: Optional[str] = None


class GenerateTripResponse(BaseModel):
    """Response model for trip generation."""

    trip_data: dict


@function_tool
def log_planning_step(step_name: str, details: str) -> str:
    """Log important steps during the travel planning process.

    Args:
        step_name: Name of the planning step (e.g., "Destination Analysis", "Budget Calculation")
        details: Details about what was done in this step

    Returns:
        Confirmation message indicating the step was logged
    """
    logger.info(f"[Travel Planning] {step_name}: {details}")
    return f"Logged: {step_name}"


@function_tool
async def searchFlights(flight_request: FlightRequest) -> list[dict]:
    """Search for flights based on the provided flight request.

    Args:
        flight_request: FlightRequest object containing flight parameters:
            - origin: Origin airport code
            - destination: Destination airport code
            - outbound_date: Outbound date
            - return_date: Return date

    Returns:
        A list of formatted flight options with airline, price, duration, stops, etc.

    Raises:
        Exception: If the search fails or API key is missing
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable is not set")

    search_params = {
        "api_key": api_key,
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": flight_request.origin.strip().upper(),
        "arrival_id": flight_request.destination.strip().upper(),
        "outbound_date": flight_request.outbound_date,
        "return_date": flight_request.return_date,
        "currency": "USD",
    }

    logger.info(f"Searching flights with params: {search_params}")
    search_results = serpapi.search(search_params)

    # Process and limit results for the agent
    best_flights = search_results.get("best_flights", [])
    other_flights = search_results.get("other_flights", [])
    all_flights = (best_flights + other_flights)[:10]  # Get top 10

    formatted_options = []
    for flight in all_flights:
        if not flight.get("flights"):
            continue

        first_leg = flight["flights"][0]
        num_flights = len(flight["flights"])
        stops = "Nonstop" if num_flights == 1 else f"{num_flights - 1} stops"

        formatted_options.append({
            "airline": first_leg.get("airline"),
            "price": f"${flight.get('price')}",
            "duration": f"{flight.get('total_duration')} min",
            "stops": stops,
            "departure": first_leg.get("departure_airport", {}).get("time"),
            "arrival": first_leg.get("arrival_airport", {}).get("time"),
            "class": first_leg.get("travel_class"),
        })

    logger.info(f"Found {len(formatted_options)} flight options")
    return formatted_options


@function_tool
async def searchHotels(hotel_request: HotelRequest) -> list[dict]:
    """Search for hotels based on the provided hotel request.

    Args:
        hotel_request: HotelRequest object containing hotel parameters:
            - location: Hotel location or city name
            - check_in_date: Check-in date in YYYY-MM-DD format
            - check_out_date: Check-out date in YYYY-MM-DD format

    Returns:
        A list of formatted hotel options with name, price, rating, amenities, etc.

    Raises:
        Exception: If the search fails or API key is missing
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable is not set")

    search_params = {
        "api_key": api_key,
        "engine": "google_hotels",
        "hl": "en",
        "gl": "us",
        "q": hotel_request.location,
        "check_in_date": hotel_request.check_in_date,
        "check_out_date": hotel_request.check_out_date,
        "currency": "USD",
    }

    logger.info(f"Searching hotels with params: {search_params}")
    search_results = serpapi.search(search_params)

    properties = search_results.get("properties", [])[:10]  # Get top 10
    formatted_options = []
    for prop in properties:
        formatted_options.append({
            "name": prop.get("name"),
            "price": prop.get("rate_per_night", {}).get("lowest"),
            "rating": prop.get("overall_rating"),
            "reviews": prop.get("reviews"),
            "amenities": prop.get("amenities", [])[:5],
            "link": prop.get("link"),
        })

    logger.info(f"Found {len(formatted_options)} hotel options")
    return formatted_options


@router.post("/generate-trip")
async def generate_trip(request: GenerateTripRequest) -> dict:
    """Generate a comprehensive trip itinerary using OpenAI agent.

    The agent autonomously handles travel planning by:
    - Parsing natural language travel requests
    - Extracting key travel parameters (dates, locations, preferences)
    - Making intelligent defaults when information is missing
    - Generating detailed, structured travel itineraries

    Args:
        request: GenerateTripRequest containing the user's travel prompt and optional sessionId

    Returns:
        Dictionary containing the generated itinerary and sessionId

    Raises:
        HTTPException: If trip generation fails
    """
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%B %Y")

    # Comprehensive agentic instructions
    instructions = f"""You are an expert AI Travel Planning Assistant with deep knowledge of global destinations, travel logistics, and personalized trip planning.

**Your Core Capabilities:**
- Parse natural language travel requests and extract all relevant details
- Understand implicit preferences and make intelligent recommendations
- Create comprehensive, day-by-day travel itineraries
- Provide reasoning for all recommendations
- Consider budget, seasonality, and traveler preferences
- Log important planning steps using the log_planning_step tool to track your progress
- Use the **searchFlights** tool to find real-time flight options for the user's destination and travel dates
- Use the **searchHotels** tool to find real-time hotel options for the user's destination and stay dates


**Current Context:**
- Today's date: {current_date}
- Current month: {current_month}

**Your Task:**
Analyze the user's travel request and create a comprehensive travel plan. Extract and infer:

1. **Travel Details:**
   - Origin city/airport (default: San Francisco/SFO if not specified)
   - Destination city/country
   - Travel dates (if relative like "next month", calculate from today's date)
   - Trip duration (default: 7 days if not specified)
   - Number of travelers (default: 1-2 if not specified)
   - Budget level (economy/moderate/luxury - infer from context)

2. **Preferences:**
   - Travel style (adventure, relaxation, cultural, romantic, family, etc.)
   - Accommodation preferences (hotel, boutique, resort, etc.)
   - Activity interests (sightseeing, food, nature, shopping, etc.)
   - Dietary restrictions or special needs

**Output Format:**
Generate a detailed, well-structured travel itinerary in markdown format with the following sections:

# Trip Overview
- **Destination:** [City, Country]
- **Origin:** [Departure City]
- **Duration:** [X days, Y nights]
- **Travel Dates:** [Start Date] to [End Date]
- **Traveler(s):** [Number and type]
- **Budget Level:** [Economy/Moderate/Luxury]
- **Trip Style:** [Adventure/Relaxation/Cultural/etc.]

---

# Flight Options & Recommendations

**Available Flight Options:**
[List at least 3 flight options found from searchFlights tool. For each, include:]
- **[Airline]** - [Price] ([Stops], [Duration])
- **Route:** [Origin] to [Destination]
- **Schedule:** [Departure Time] - [Arrival Time]

**Recommended Flight:**
- **Airline:** [Recommended Airline]
- **Reasoning:** [Why this is the best recommendation among the options]

---

# Accommodation Options & Recommendations

**Available Hotel Options:**
[List at least 3 hotel options found from searchHotels tool. For each, include:]
- **[Hotel Name]** ([Rating] stars) - [Price per night]
- **Key Amenities:** [List 2-3 key amenities]
- **Link:** [Link to hotel]

**Recommended Stay:**
- **Hotel:** [Recommended Hotel Name]
- **Reasoning:** [Why this is the best recommendation among the options]

---

# Day-by-Day Itinerary

## Day 1: [Date] - Arrival & [Theme]
**Morning:**
- Arrive at [Airport Name]
- Transportation to hotel (recommended: [method], ~[time], ~$[cost])
- Check-in at hotel

**Afternoon:**
- Lunch at [Restaurant/Area] - [Cuisine type]
- [Activity/Attraction] ([Duration], [Cost if applicable])

**Evening:**
- [Evening activity]
- Dinner recommendation: [Restaurant] - [Why recommended]

**Tips:** [Local tips, what to know, what to avoid]

## Day 2: [Date] - [Theme]
[Continue with similar structure for each day]

[... Continue for all days of the trip ...]

## Day [Last]: [Date] - Departure
**Morning:**
- Breakfast at hotel
- Last-minute shopping/activities
- Check-out

**Afternoon:**
- Transportation to airport
- Depart for [Origin]

---

# Must-Visit Attractions

1. **[Attraction Name]**
   - **Best time to visit:** [Time/Day]
   - **Duration:** [Hours]
   - **Cost:** [Price/Free]
   - **Why visit:** [Reasoning]

[List 5-8 top attractions]

---

# Dining Recommendations

**Breakfast Spots:**
- [Restaurant 1] - [Specialty]
- [Restaurant 2] - [Specialty]

**Lunch Options:**
- [Restaurant 1] - [Cuisine, Price range]
- [Restaurant 2] - [Cuisine, Price range]

**Dinner Experiences:**
- [Restaurant 1] - [Why recommended, Price range]
- [Restaurant 2] - [Why recommended, Price range]

**Local Specialties to Try:**
- [Dish 1]
- [Dish 2]
- [Dish 3]

---

# Transportation Tips

- **From Airport:** [Best options with estimated costs]
- **Getting Around:** [Metro/Bus/Taxi/Walking recommendations]
- **Transportation Passes:** [Any day passes or tourist cards worth buying]
- **Estimated Daily Transport Cost:** $[Amount]

---

# Budget Estimate

| Category | Estimated Cost |
|----------|---------------|
| Flights (roundtrip) | $[Amount] |
| Accommodation ([X] nights) | $[Amount] |
| Meals ([X] days) | $[Amount] |
| Activities & Attractions | $[Amount] |
| Transportation | $[Amount] |
| Miscellaneous | $[Amount] |
| **Total Estimated** | **$[Total]** |

*Note: Prices are estimates and may vary based on season and booking time.*

---

# Essential Travel Tips

**Before You Go:**
- [Visa requirements if applicable]
- [Health/vaccination recommendations]
- [Currency and exchange tips]
- [Power adapter needs]

**Packing Essentials:**
- [Season-appropriate clothing recommendations]
- [Special items needed for planned activities]

**Local Customs:**
- [Important cultural norms to know]
- [Tipping practices]
- [Common phrases in local language]

**Safety Tips:**
- [Areas to avoid]
- [Emergency numbers]
- [Common scams to watch out for]

**Best Time to Visit:**
- [Seasonal considerations for the travel dates]
- [Weather expectations]

---

# Pro Tips

- [Insider tip 1]
- [Insider tip 2]
- [Insider tip 3]
- [Money-saving tip]
- [Time-saving tip]

---

**Have an amazing trip! This itinerary is a flexible guide - feel free to adjust based on your energy levels and interests each day.**

---

**Important Guidelines:**
- Be specific with dates, calculating from today's date ({current_date}) when user provides relative dates
- Provide realistic time estimates and costs
- Consider seasonality and weather for the destination
- Make intelligent assumptions when information is missing, but note them
- Tailor recommendations to the inferred travel style and budget
- Include practical, actionable advice
- Do NOT use emojis in the itinerary. ensure it is visually appealing through good use of markdown and structure instead.
- Provide reasoning for major recommendations
"""

    try:
        # Create the agent with comprehensive instructions and tools
        agent = Agent(
            name="Expert Travel Planning Assistant",
            model="gpt-5.2",
            instructions=instructions,
            tools=[log_planning_step, searchFlights, searchHotels]
        )

        session_id = request.sessionId
        if session_id is None:
            session_id = str(uuid.uuid4())

        session = SQLiteSession(session_id=session_id, db_path="sessions.db")

        # Run the agent with the user's prompt
        result = await Runner.run(agent, request.prompt, session=session)

        logger.info(f"Trip generation completed for session: {session_id}")

        # Return structured response
        return {
            "itinerary": result.final_output,
            "sessionId": session_id,
        }

    except Exception as e:
        # Handle errors gracefully
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trip itinerary: {str(e)}"
        )
