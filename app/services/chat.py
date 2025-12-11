from langchain_google_genai import ChatGoogleGenerativeAI
import uuid
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.models.model import ChatsHistory, ChatRequest, KeepChatRequest

load_dotenv()

# TODO: Use Supabase to store the chats history.
database: ChatsHistory = ChatsHistory(
    chats_history={
        "e1a1a51f-456d-4885-ad56-7290354b6d25": [
            SystemMessage(content="You are a helpful travel assistant."),
            HumanMessage(
                content="You are given a detailed itinerary and a conversation message..."),
            AIMessage(
                content="Here is a itinerary for your trip to Paris:..."),
            HumanMessage(
                content="Could I get more coffee suggestions near the hotel?"),
            AIMessage(
                content="Here are some coffee suggestions near the hotel:..."),
        ]
    }
)


class ChatService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    def start_chat(self, chat_request: ChatRequest) -> AIMessage:
        new_chat_id = str(uuid.uuid4())

        prompt = f"""
        You are given a detailed itinerary and a conversation message. You need to respond to the conversation message based on the itinerary.
        The itinerary is: {chat_request.itinerary}
        The human message is: {chat_request.human_message}
        """
        database.chats_history[new_chat_id] = [
            SystemMessage(content="You are a helpful travel assistant."),
            HumanMessage(content=prompt),
        ]
        chat_response = self.llm.invoke(database.chats_history[new_chat_id])

        new_message = AIMessage(content=chat_response.content)

        # Append the chat response to the database
        database.chats_history[new_chat_id].append(
            new_message)

        response = {
            "chat_id": new_chat_id,
            "response": new_message
        }
        return response

    def keep_chat(self, keep_chat_request: KeepChatRequest) -> AIMessage:
        chats_history = database.chats_history[keep_chat_request.chat_id]
        chats_history.append(HumanMessage(
            content=keep_chat_request.human_message))
        chat_response = self.llm.invoke(chats_history)

        # Append the chat response to the database
        new_message = AIMessage(content=chat_response.content)
        database.chats_history[keep_chat_request.chat_id].append(new_message)
        response = {
            "chat_id": keep_chat_request.chat_id,
            "response": new_message
        }
        return response

    def get_chat(self, chat_id: str) -> list[SystemMessage | HumanMessage | AIMessage]:
        return database.chats_history[chat_id]
