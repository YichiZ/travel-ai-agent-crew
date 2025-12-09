import { useState } from 'react';
import './SearchForm.css';

const SearchForm = ({ onSearch, isLoading }) => {
  const [conversationText, setConversationText] = useState('');

  const handleChange = (e) => {
    setConversationText(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (conversationText.trim()) {
      onSearch(conversationText);
    }
  };

  return (
    <div className="search-form-container">
      <h2>Plan Your Trip</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-section">
          <label htmlFor="conversation">Tell us about your trip</label>
          <textarea
            id="conversation"
            name="conversation"
            value={conversationText}
            onChange={handleChange}
            placeholder="e.g., I want to fly from San Francisco to Las Vegas on December 1st and return on December 15th. I'm looking for a hotel in Las Vegas for those dates."
            rows={10}
            required
            className="conversation-textarea"
          />
        </div>

        <button type="submit" className="search-button" disabled={isLoading || !conversationText.trim()}>
          {isLoading ? 'Searching...' : 'Search Trips'}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;
