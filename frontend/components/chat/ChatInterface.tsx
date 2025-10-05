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
      const response = await chatAPI.sendMessage(content, currentSession?.id);

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
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
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
        <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-2xl mx-auto space-y-4">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-accent-100 to-accent-200 flex items-center justify-center">
                  <span className="text-white font-bold text-2xl">K</span>
                </div>
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
                  Welcome to K-OSMOS
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Your AI-powered research assistant for space biology. Ask me anything about
                  microgravity effects, space missions, or biological research in space.
                </p>
                <div className="text-xs text-gray-400 dark:text-gray-500 italic mt-2">
                  Fun fact: Did you know astronauts can't cry properly in space? Tears don't fall - they just form bubbles around your eyes! 
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6">
                  {[
                    'Effects of microgravity on bone density',
                    'ISS cardiovascular research studies',
                    'Why do astronauts grow taller in space?',
                    'Space lettuce: tastier than Earth lettuce?',
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(suggestion)}
                      className="card-hover p-4 text-left text-sm"
                    >
                      <p className="font-medium text-accent-200">{suggestion}</p>
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
            <div className="max-w-4xl mx-auto space-y-6">
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
          <div className="max-w-4xl mx-auto px-4 py-4">
            <InputBox onSend={handleSendMessage} disabled={isLoading} />
          </div>
        </div>
      </div>

      {/* Sources Panel */}
      {sources.length > 0 && <SourcesPanel sources={sources} />}
    </div>
  );
}
