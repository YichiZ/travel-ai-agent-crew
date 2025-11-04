import ReactMarkdown from 'react-markdown';
import './Itinerary.css';

const Itinerary = ({ itinerary }) => {
  if (!itinerary) {
    return null;
  }

  return (
    <div className="itinerary-container">
      <h2>Your Personalized Itinerary</h2>
      <div className="itinerary-content markdown-content">
        <ReactMarkdown>{itinerary}</ReactMarkdown>
      </div>
    </div>
  );
};

export default Itinerary;
