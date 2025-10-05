'use client';

import { useState, useRef, useEffect } from 'react';
import { useStore } from '@/store/useStore';
import { chatAPI } from '@/utils/api';
import MessageBubble from './MessageBubble';
import InputBox from './InputBox';
import SourcesPanel from './SourcesPanel';
import LoadingIndicator from './LoadingIndicator';
import NASAFacts from '@/components/ui/NASAFacts';
import { Message, Source } from '@/types';

export default function ChatInterface() {
  const { messages, addMessage, isLoading, setLoading, currentSession, updateSessionTitle } = useStore();
  const [sources, setSources] = useState<Source[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setLoading(true);

    // Update session title if this is the first message
    if (currentSession && currentSession.title === 'New Conversation' && messages.length === 0) {
      const title = content.length > 50 ? content.substring(0, 47) + '...' : content;
      updateSessionTitle(currentSession.id, title);
    }

    try {
      console.log('Sending message to API:', content);
      const response = await chatAPI.sendMessage(content, currentSession?.id);
      console.log('API response received:', {
        responseLength: response.response?.length,
        sourcesCount: response.sources?.length,
        entitiesCount: response.entities?.length
      });

      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        sources: response.sources,
        entities: response.entities,
      };

      addMessage(assistantMessage);
      setSources(response.sources || []);
    } catch (error: any) {
      console.error('Error sending message:', error);
      console.error('Error details:', {
        message: error?.message,
        code: error?.code,
        response: error?.response?.data,
        status: error?.response?.status
      });
      
      let errorContent = 'Sorry, I encountered an error processing your request. Please try again.';
      
      // Add more specific error information for debugging
      if (error?.code === 'ECONNABORTED') {
        errorContent = 'Request timeout. The AI is taking longer than expected to respond. Please try a shorter question.';
      } else if (error?.response?.status >= 500) {
        errorContent = 'Server error occurred. Please try again in a moment.';
      } else if (error?.response?.status === 404) {
        errorContent = 'API endpoint not found. Please check if the backend server is running.';
      } else if (error?.response?.data?.detail) {
        errorContent = `API Error: ${JSON.stringify(error.response.data.detail)}`;
      }
      
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: errorContent,
        timestamp: new Date(),
      };
      
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center px-4 py-6">
              <div className="text-center max-w-2xl mx-auto space-y-6">
                <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-gray-700 to-gray-800 dark:from-gray-600 dark:to-gray-700 flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-2xl">K</span>
                </div>
                <div className="space-y-2">
                  <h2 className="text-3xl font-semibold text-gray-900 dark:text-gray-100">
                    Welcome to K-OSMOS
                  </h2>
                  <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                    Your AI-powered research assistant for space biology. Ask me anything about
                    microgravity effects, space missions, or biological research in space.
                  </p>
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400 italic bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
                  💡 Fun fact: Did you know astronauts can't cry properly in space? Tears don't fall - they just form bubbles around your eyes! 
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
                  {[
                    'Effects of microgravity on bone density',
                    'ISS cardiovascular research studies',
                    'Why do astronauts grow taller in space?',
                    'Space lettuce: tastier than Earth lettuce?',
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(suggestion)}
                      className="p-4 text-left text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:border-accent-200 dark:hover:border-accent-100 hover:shadow-sm transition-all duration-200 group"
                    >
                      <p className="font-medium text-gray-800 dark:text-gray-200 group-hover:text-accent-200 dark:group-hover:text-accent-100 transition-colors">
                        {suggestion}
                      </p>
                    </button>
                  ))}
                </div>
                
                {/* NASA Fun Facts */}
                <div className="mt-8 max-w-md mx-auto">
                  <NASAFacts />
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto px-4 py-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && <LoadingIndicator />}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <InputBox onSend={handleSendMessage} disabled={isLoading} />
          </div>
        </div>
      </div>

      {/* Sources Panel */}
      {sources.length > 0 && <SourcesPanel sources={sources} />}
    </div>
  );
}
