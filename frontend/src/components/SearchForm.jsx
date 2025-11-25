import { useState } from 'react';
import './SearchForm.css';

const SearchForm = ({ onSearch, isLoading }) => {
  const [formData, setFormData] = useState({
    origin: 'SFO',
    destination: 'LAS',
    outboundDate: '2025-12-01',
    returnDate: '2025-12-15',
    location: 'Las Vegas',
    checkInDate: '',
    checkOutDate: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const flightRequest = {
      origin: formData.origin,
      destination: formData.destination,
      outbound_date: formData.outboundDate,
      return_date: formData.returnDate,
    };

    const hotelRequest = formData.location ? {
      location: formData.location || formData.destination,
      check_in_date: formData.checkInDate || formData.outboundDate,
      check_out_date: formData.checkOutDate || formData.returnDate,
    } : null;

    onSearch(flightRequest, hotelRequest);
  };

  return (
    <div className="search-form-container">
      <h2>Plan Your Trip</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-section">
          <h3>Flight Details</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="origin">From (Airport Code)</label>
              <input
                type="text"
                id="origin"
                name="origin"
                value={formData.origin}
                onChange={handleChange}
                placeholder="e.g., SFO"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="destination">To (Airport Code)</label>
              <input
                type="text"
                id="destination"
                name="destination"
                value={formData.destination}
                onChange={handleChange}
                placeholder="e.g., JFK"
                required
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="outboundDate">Departure Date</label>
              <input
                type="date"
                id="outboundDate"
                name="outboundDate"
                value={formData.outboundDate}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="returnDate">Return Date</label>
              <input
                type="date"
                id="returnDate"
                name="returnDate"
                value={formData.returnDate}
                onChange={handleChange}
                required
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Hotel Details (Optional)</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g., New York (optional)"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="checkInDate">Check-in Date</label>
              <input
                type="date"
                id="checkInDate"
                name="checkInDate"
                value={formData.checkInDate}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="checkOutDate">Check-out Date</label>
              <input
                type="date"
                id="checkOutDate"
                name="checkOutDate"
                value={formData.checkOutDate}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        <button type="submit" className="search-button" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search Trips'}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;
