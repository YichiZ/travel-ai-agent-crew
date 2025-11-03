# Travel AI Agent Crew

Multi agent app for create travel itinerary using Gemini and CrewAI.

## Getting Started

1. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

1. **Install dependencies**
   Using uv (faster):

   ```bash
   uv pip install -r requirements.txt
   ```

   Using standard pip:

   ```bash
   pip install -r requirements.txt
   ```

1. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   SERP_API_KEY=your_serpapi_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY="" # Keep empty string
   CREWAI_TRACING_ENABLED=true
   ```

### Running the Application

**Using uv (faster):**

```bash
uv run main.py
```

**Standard:**

```bash
python main.py
```

Play with the API at http://localhost:8000/docs.

## Features

For a list of features, see [FEATURES.md](FEATURES.md)
