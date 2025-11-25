# Travel AI Agent Crew

AI-Powered Multi-Agent Travel App for Flights, Hotels, and Itineraries.

## Getting Started

1. **Install dependencies**

   Using uv (recommended, faster):

   ```bash
   uv sync
   ```

   This will create a virtual environment and install all dependencies from `pyproject.toml` and `uv.lock`.

   Using standard pip:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Configure environment variables**

   Create a `.env` file in the root directory:

   ```env
   SERP_API_KEY=your_serpapi_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY="" # Keep empty string
   CREWAI_TRACING_ENABLED=true
   ```

### Running the Application

**Using uv (recommended):**

```bash
uv run fastapi dev
```

**Standard:**

```bash
source .venv/bin/activate
python app/main.py
```

Play with the API at http://localhost:8000/docs.

## Deployment
Use the `deploy.sh` file to push the backend docker to AWS ECR, then use AWS App Runner to deploy the image.

Local:
```bash
# Build the image
docker build -t travel-ai-agent-crew-api .

# Run the container
docker run -p 8080:8080 travel-ai-agent-crew-api
```

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
