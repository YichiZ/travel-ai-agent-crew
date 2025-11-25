# Travel AI Agent Crew

Multi agent app for create travel itinerary using Gemini and CrewAI.

## 🌟 Features

- **Flight Search & Recommendations**: Search flights via SerpAPI and get AI-powered analysis comparing options based on price, duration, stops, and comfort
- **Hotel Search & Recommendations**: Find hotels and receive intelligent recommendations considering price, rating, location, and amenities
- **Complete Travel Search**: Parallel search for both flights and hotels with comprehensive AI analysis
- **Itinerary Generation**: Generate detailed day-by-day travel itineraries with activities, attractions, and restaurant recommendations
- **Multi-Agent System**: Specialized AI agents for flights, hotels, and travel planning using CrewAI framework

## 🏗️ Architecture

### Project Structure

```
travel-ai-agent-crew/
├── app/
│   ├── main.py            # FastAPI application & endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── model.py       # Pydantic models & enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crew.py        # CrewAI service (AI agents & tasks)
│   │   └── serp.py        # SerpAPI integration
│   └── helpers/
│       ├── __init__.py
│       └── helper.py      # Utility functions
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (API keys)
```

### AI Agent Workflow

The application uses a **multi-agent architecture** with three specialized AI agents:

1. **Flight Analyst Agent**: Analyzes flight options and recommends the best choice
2. **Hotel Analyst Agent**: Evaluates hotel options based on multiple factors
3. **Travel Planner Agent**: Creates comprehensive itineraries with day-by-day breakdowns

Each agent is powered by Google Gemini 2.5 Flash and uses structured task workflows via CrewAI.

## 📚 API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Endpoints

#### 1. Search Flights

**POST** `/search_flights/`

Search for flights and get AI-powered recommendations.

**Request Body:**

```json
{
  "origin": "SFO",
  "destination": "JFK",
  "outbound_date": "2025-12-01",
  "return_date": "2025-12-15"
}
```

**Response:**

```json
{
  "flights": [...],
  "hotels": [],
  "ai_flight_recommendation": "Based on the analysis...",
  "ai_hotel_recommendation": "",
  "itinerary": ""
}
```

#### 2. Search Hotels

**POST** `/search_hotels/`

Search for hotels and receive AI recommendations.

**Request Body:**

```json
{
  "location": "New York",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-15"
}
```

#### 3. Complete Travel Search

**POST** `/complete_search/`

Perform parallel flight and hotel searches with full AI analysis and itinerary generation.

**Request Body:**

```json
{
  "origin": "SFO",
  "destination": "JFK",
  "outbound_date": "2025-12-01",
  "return_date": "2025-12-15",
  "location": "New York",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-15"
}
```

**Response:**

```json
{
  "flights": [...],
  "hotels": [...],
  "ai_flight_recommendation": "Detailed flight analysis...",
  "ai_hotel_recommendation": "Comprehensive hotel review...",
  "itinerary": "# 14-Day New York Itinerary\n\n## Day 1..."
}
```

#### 4. Generate Itinerary

**POST** `/generate_itinerary/`

Generate a detailed itinerary based on provided flight and hotel information.

**Request Body:**

```json
{
  "destination": "New York",
  "flights": "Flight details text...",
  "hotels": "Hotel details text...",
  "check_in_date": "2025-12-01",
  "check_out_date": "2025-12-15"
}
```

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **AI Framework**: CrewAI
- **LLM**: Google Gemini 2.5 Flash
- **Search API**: SerpAPI (Google Flights/Hotels)
- **Data Validation**: Pydantic
- **Async Support**: asyncio
- **Environment Management**: python-dotenv

## 🧩 Key Components

### Models (`models/model.py`)

- **WorkflowType**: Enum for FLIGHT, HOTEL, TRAVEL workflows
- **CreateTaskOptions**: Pydantic model for task configuration
- **FlightRequest/HotelRequest**: API request models
- **AIResponse**: Unified API response model

### Services

#### CrewAI Service (`services/crew.py`)

- Manages three specialized AI agents
- Handles task creation and crew orchestration
- Provides recommendations and itinerary generation
- Uses Google Gemini for AI processing

#### SerpAPI Service (`services/serp.py`)

- Integrates with SerpAPI for real-time search
- Fetches flight and hotel data
- Formats results for AI analysis

### Helpers (`helpers/helper.py`)

- Utility functions for data formatting
- Prepares search results for AI consumption

## 🔒 Security Notes

- Never commit your `.env` file
- Keep API keys secure and rotate them regularly
- The `.gitignore` file is configured to exclude sensitive files

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👤 Author

**YichiZ**

- GitHub: [@YichiZ](https://github.com/YichiZ)

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent framework
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [SerpAPI](https://serpapi.com/) for search data
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

---

**Note**: This project requires valid API keys for SerpAPI and Google Gemini. Make sure to set them up in your `.env` file before running the application.
