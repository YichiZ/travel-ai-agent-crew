import ReactMarkdown from 'react-markdown';
import './HotelResults.css';

const HotelResults = ({ hotels, recommendation }) => {
  if (!hotels || hotels.length === 0) {
    return null;
  }

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={`full-${i}`} className="star full">★</span>);
    }
    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">★</span>);
    }

    return stars;
  };

  const formatPrice = (price) => {
    if (!price) return '';
    // If price already has a dollar sign, return as is
    if (price.toString().includes('$')) return price;
    // Otherwise, add dollar sign
    return `$${price}`;
  };

  return (
    <div className="hotel-results">
      <h2>Hotel Options</h2>

      {recommendation && (
        <div className="ai-recommendation">
          <h3>AI Recommendation</h3>
          <div className="markdown-content">
            <ReactMarkdown>{recommendation}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="hotels-grid">
        {hotels.map((hotel, index) => (
          <div key={index} className="hotel-card">
            <div className="hotel-header">
              <h3>{hotel.name}</h3>
              <div className="hotel-rating">
                {renderStars(hotel.rating)}
                <span className="rating-number">{hotel.rating.toFixed(1)}</span>
              </div>
            </div>

            <div className="hotel-details">
              <div className="hotel-location">
                <span className="location-icon">📍</span>
                <span>{hotel.location}</span>
              </div>

              <div className="hotel-price">
                <span className="price-label">Price per night</span>
                <span className="price-value">{formatPrice(hotel.price)}</span>
              </div>
            </div>

            {hotel.link && (
              <div className="hotel-footer">
                <a
                  href={hotel.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="view-hotel-btn"
                >
                  View Details
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HotelResults;
