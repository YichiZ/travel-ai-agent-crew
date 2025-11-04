import ReactMarkdown from 'react-markdown';
import './FlightResults.css';

const FlightResults = ({ flights, recommendation }) => {
  if (!flights || flights.length === 0) {
    return null;
  }

  const formatPrice = (price) => {
    if (!price) return '';
    // If price already has a dollar sign, return as is
    if (price.toString().includes('$')) return price;
    // Otherwise, add dollar sign
    return `$${price}`;
  };

  return (
    <div className="flight-results">
      <h2>Flight Options</h2>

      {recommendation && (
        <div className="ai-recommendation">
          <h3>AI Recommendation</h3>
          <div className="markdown-content">
            <ReactMarkdown>{recommendation}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="flights-grid">
        {flights.map((flight, index) => (
          <div key={index} className="flight-card">
            <div className="flight-header">
              {flight.airline_logo && (
                <img
                  src={flight.airline_logo}
                  alt={flight.airline}
                  className="airline-logo"
                />
              )}
              <h3>{flight.airline}</h3>
            </div>

            <div className="flight-details">
              <div className="flight-time">
                <div className="time-info">
                  <span className="label">Departure</span>
                  <span className="time">{flight.departure}</span>
                </div>
                <div className="flight-duration">
                  <div className="duration-line"></div>
                  <span>{flight.duration}</span>
                </div>
                <div className="time-info">
                  <span className="label">Arrival</span>
                  <span className="time">{flight.arrival}</span>
                </div>
              </div>

              <div className="flight-meta">
                <div className="meta-item">
                  <span className="meta-label">Stops:</span>
                  <span className="meta-value">{flight.stops}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Class:</span>
                  <span className="meta-value">{flight.travel_class}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Return:</span>
                  <span className="meta-value">{flight.return_date}</span>
                </div>
              </div>
            </div>

            <div className="flight-footer">
              <div className="price">{formatPrice(flight.price)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlightResults;
