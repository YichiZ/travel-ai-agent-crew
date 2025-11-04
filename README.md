# Travel AI Agent Crew

AI-Powered Multi-Agent Travel App for Flights, Hotels, and Itineraries

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

## Frontend

1. **Navigate to frontend and install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment (optional)**

   ```bash
   cp .env.example .env
   ```

3. **Run the frontend**

   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## Features

For a list of features, see [FEATURES.md](FEATURES.md)
