import { useState } from 'react';
import SearchForm from './components/SearchForm';
import FlightResults from './components/FlightResults';
import HotelResults from './components/HotelResults';
import Itinerary from './components/Itinerary';
import { generate_itinerary_from_conversation } from './services/api';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleSearch = async (conversationText) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await generate_itinerary_from_conversation(conversationText);
      setResults(data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'An error occurred while searching. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Travel Planner</h1>
        <p>Powered by AI to find the best flights, hotels, and create your perfect itinerary</p>
      </header>

      <main className="app-main">
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Searching for the best travel options and generating your itinerary...</p>
            <p className="loading-subtext">This may take a moment as our AI analyzes options</p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {results && !isLoading && (
          <div className="results-container">
            <FlightResults
              flights={results.flights}
              recommendation={results.ai_flight_recommendation}
            />

            <HotelResults
              hotels={results.hotels}
              recommendation={results.ai_hotel_recommendation}
            />

            <Itinerary itinerary={results.itinerary} />
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by AI and SERP API</p>
      </footer>
    </div>
  );
}

export default App;
