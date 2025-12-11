import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const searchCompleteTravel = async (
  flightRequest,
  hotelRequest = null
) => {
  try {
    const response = await api.post("/complete_search/", {
      flight_request: flightRequest,
      hotel_request: hotelRequest,
    });
    return response.data;
  } catch (error) {
    console.error("Error searching travel:", error);
    throw error;
  }
};

export const generate_itinerary_from_conversation = async (
  conversation_text: string
) => {
  try {
    const response = await api.post("/generate_itinerary_from_conversation/", {
      conversation_text: conversation_text,
    });
    return response.data;
  } catch (error) {
    console.error("Error generating itinerary from conversation:", error);
    throw error;
  }
};

export const start_chat = async (itinerary: string, human_message: string) => {
  try {
    const response = await api.post("/start_chat/", {
      itinerary: itinerary,
      human_message: human_message,
    });
    return response.data;
  } catch (error) {
    console.error("Error starting chat:", error);
    throw error;
  }
};

export const keep_chat = async (chat_id: string, human_message: string) => {
  try {
    const response = await api.post("/keep_chat/", {
      chat_id: chat_id,
      human_message: human_message,
    });
    return response.data;
  } catch (error) {
    console.error("Error keeping chat:", error);
    throw error;
  }
};

export default api;
