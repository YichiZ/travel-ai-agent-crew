import { useState } from 'react';
import SearchForm from './components/SearchForm';
import Itinerary from './components/Itinerary';
import Tabs from './components/Tabs';
import ItineraryChatTab from './components/ItineraryChatTab';
import { generate_itinerary_from_conversation } from './services/api';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [tabs, setTabs] = useState([]);
  const [activeTab, setActiveTab] = useState(null);

  const extractDestination = (data) => {
    // Use itinerary_json.arrival_location (now required field)
    return data.itinerary_json.arrival_location;
  };

  const handleSearch = async (conversationText) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await generate_itinerary_from_conversation(conversationText);
      setResults(data);
      
      // Extract destination from itinerary_json (most reliable source)
      const destination = extractDestination(data);
      
      // Create a new tab for this itinerary
      const newTabId = `tab-${Date.now()}`;
      const newTab = {
        id: newTabId,
        label: `Trip to ${destination}`,
        itinerary: data.itinerary,
        chatId: null,
        messages: [],
        isLoading: false
      };
      
      setTabs(prev => [...prev, newTab]);
      setActiveTab(newTabId);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'An error occurred while searching. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
  };

  const handleChatUpdate = (chatId, messages) => {
    // Find the tab that matches the current active tab and update it
    setTabs(prev => prev.map(tab => 
      tab.id === activeTab 
        ? { ...tab, chatId, messages }
        : tab
    ));
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

        {tabs.length > 0 && (
          <Tabs
            tabs={tabs.map(tab => ({
              id: tab.id,
              label: tab.label,
              content: (
                <ItineraryChatTab
                  key={tab.id}
                  itinerary={tab.itinerary}
                  chatId={tab.chatId}
                  messages={tab.messages}
                  onChatUpdate={handleChatUpdate}
                />
              )
            }))}
            activeTab={activeTab}
            onTabChange={handleTabChange}
          />
        )}

        {results && !isLoading && tabs.length === 0 && (
          <div className="results-container">
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
