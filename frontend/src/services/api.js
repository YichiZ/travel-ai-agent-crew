import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchCompleteTravel = async (flightRequest, hotelRequest = null) => {
  try {
    const response = await api.post('/complete_search/', {
      flight_request: flightRequest,
      hotel_request: hotelRequest,
    });
    return response.data;
  } catch (error) {
    console.error('Error searching travel:', error);
    throw error;
  }
};

export const generate_itinerary_from_conversation = async (conversation_text) => {
  try {
    const response = await api.post('/generate_itinerary_from_conversation/', {
      conversation_text: conversation_text,
    });
    return response.data;
  } catch (error) {
    console.error('Error generating itinerary from conversation:', error);
    throw error;
  }
};

export default api;
