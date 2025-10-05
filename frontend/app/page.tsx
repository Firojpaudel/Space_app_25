'use client';

import { useEffect } from 'react';
import { useStore } from '@/store/useStore';
import Navbar from '@/components/layout/Navbar';
import Sidebar from '@/components/layout/Sidebar';
import ChatInterface from '@/components/chat/ChatInterface';
import { MessageSquare } from 'lucide-react';

export default function Home() {
  const { sidebarOpen, createNewSession } = useStore();

  useEffect(() => {
    // Create initial session on mount
    createNewSession();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <Navbar />
      
      <div className="flex pt-16">
        <Sidebar />
        
        <main
          className={`flex-1 smooth-transition ${
            sidebarOpen ? 'ml-80' : 'ml-0'
          }`}
        >
          <ChatInterface />
        </main>
      </div>

      {/* Floating Action Button for New Chat */}
      <button
        onClick={createNewSession}
        className="fab group"
        aria-label="New chat"
      >
        <MessageSquare className="w-6 h-6 group-hover:scale-110 transition-transform" />
      </button>
    </div>
  );
}
