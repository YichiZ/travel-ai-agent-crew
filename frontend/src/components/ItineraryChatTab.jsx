import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import ChatDialog from './ChatDialog';
import { start_chat, keep_chat } from '../services/api';
import './ItineraryChatTab.css';

const ItineraryChatTab = ({ itinerary, chatId: initialChatId, messages: initialMessages, onChatUpdate }) => {
  const [chatId, setChatId] = useState(initialChatId || null);
  const [messages, setMessages] = useState(initialMessages || []);
  const [isLoading, setIsLoading] = useState(false);
  const [hasStartedChat, setHasStartedChat] = useState(initialChatId !== null);
  const [initialMessage, setInitialMessage] = useState('');

  const handleStartChat = async () => {
    if (!initialMessage.trim()) {
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await start_chat(itinerary, initialMessage.trim());
      const newChatId = response.chat_id;
      // Handle response format - response.response is an AIMessage object that may be serialized
      let aiMessage = '';
      if (response.response) {
        if (typeof response.response === 'string') {
          aiMessage = response.response;
        } else if (response.response.content) {
          aiMessage = response.response.content;
        } else if (response.response.text) {
          aiMessage = response.response.text;
        }
      }
      
      setChatId(newChatId);
      setHasStartedChat(true);
      const newMessages = [
        { role: 'user', content: initialMessage.trim() },
        { role: 'ai', content: aiMessage }
      ];
      setMessages(newMessages);
      setInitialMessage(''); // Clear the input after starting chat
      
      if (onChatUpdate) {
        onChatUpdate(newChatId, newMessages);
      }
    } catch (error) {
      console.error('Error starting chat:', error);
      alert('Failed to start chat. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText) => {
    if (!chatId) {
      return;
    }

    setIsLoading(true);
    const userMessage = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await keep_chat(chatId, messageText);
      // Handle response format - response.response is an AIMessage object that may be serialized
      let aiMessage = '';
      if (response.response) {
        if (typeof response.response === 'string') {
          aiMessage = response.response;
        } else if (response.response.content) {
          aiMessage = response.response.content;
        } else if (response.response.text) {
          aiMessage = response.response.text;
        }
      }
      const newMessages = [...messages, userMessage, { role: 'ai', content: aiMessage }];
      setMessages(newMessages);
      
      if (onChatUpdate) {
        onChatUpdate(chatId, newMessages);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.slice(0, -1)); // Remove the user message on error
      alert('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="itinerary-chat-tab">
      <div className="itinerary-section">
        <h2>Your Personalized Itinerary</h2>
        <div className="itinerary-content markdown-content">
          <ReactMarkdown>{itinerary}</ReactMarkdown>
        </div>
      </div>

      <div className="chat-section">
        {!hasStartedChat ? (
          <div className="start-chat-container">
            <input
              type="text"
              value={initialMessage}
              onChange={(e) => setInitialMessage(e.target.value)}
              placeholder="Ask a question about this itinerary..."
              className="start-chat-input"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && initialMessage.trim() && !isLoading) {
                  handleStartChat();
                }
              }}
            />
            <button
              onClick={handleStartChat}
              className="start-chat-button"
              disabled={isLoading || !initialMessage.trim()}
            >
              {isLoading ? 'Starting Chat...' : 'Start Chat'}
            </button>
          </div>
        ) : (
          <ChatDialog
            chatId={chatId}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            messages={messages}
          />
        )}
      </div>
    </div>
  );
};

export default ItineraryChatTab;

