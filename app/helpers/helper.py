"""Helper functions for the Travel Planning API."""


def format_flight_data(flights):
    """Format flight data into a readable text string."""
    if not flights:
        return "No flights available."

    formatted_text = "✈️ **Available flight options**:\n\n"
    for i, flight in enumerate(flights):
        formatted_text += (
            f"**Flight {i + 1}:**\n"
            f"✈️ **Airline:** {flight.airline}\n"
            f"💰 **Price:** ${flight.price}\n"
            f"⏱️ **Duration:** {flight.duration}\n"
            f"🛑 **Stops:** {flight.stops}\n"
            f"🕔 **Departure:** {flight.departure}\n"
            f"🕖 **Arrival:** {flight.arrival}\n"
            f"💺 **Class:** {flight.travel_class}\n\n"
        )

    return formatted_text.strip()


def format_hotel_data(hotels):
    """Format hotel data into a readable text string."""
    if not hotels:
        return "No hotels available."

    formatted_text = "🏨 **Available Hotel Options**:\n\n"
    for i, hotel in enumerate(hotels):
        formatted_text += (
            f"**Hotel {i + 1}:**\n"
            f"🏨 **Name:** {hotel.name}\n"
            f"💰 **Price:** ${hotel.price}\n"
            f"⭐ **Rating:** {hotel.rating}\n"
            f"📍 **Location:** {hotel.location}\n"
        )

    return formatted_text.strip()
