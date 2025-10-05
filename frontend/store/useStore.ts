import { create } from 'zustand';
import { Theme, Message, ChatSession, SearchFilters } from '@/types';

interface AppStore {
  // Theme
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;

  // Chat
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  messages: Message[];
  isLoading: boolean;
  setCurrentSession: (session: ChatSession | null) => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  createNewSession: () => void;
  updateSessionTitle: (sessionId: string, title: string) => void;

  // Search
  searchFilters: SearchFilters;
  setSearchFilters: (filters: SearchFilters) => void;
  clearSearchFilters: () => void;

  // UI State
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppStore>((set) => ({
  // Theme
  theme: 'dark',
  setTheme: (theme) => set({ theme }),
  toggleTheme: () =>
    set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),

  // Chat
  currentSession: null,
  sessions: [
    {
      id: 'session-1',
      title: 'Microgravity Effects on Bone Density',
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'What are the effects of microgravity on bone density?',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
        },
        {
          id: 'msg-2',
          role: 'assistant',
          content: 'Microgravity has significant effects on bone density. In the weightless environment of space, astronauts experience rapid bone loss, particularly in weight-bearing bones like the spine, hips, and legs. Studies show that astronauts can lose 1-2% of bone mass per month during spaceflight, which is much faster than the typical age-related bone loss of 1-2% per year on Earth.',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000 + 30000)
        }
      ]
    },
    {
      id: 'session-2',
      title: 'ISS Plant Growth Experiments',
      createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
      updatedAt: new Date(Date.now() - 5 * 60 * 60 * 1000),
      messages: [
        {
          id: 'msg-3',
          role: 'user',
          content: 'Tell me about plant growth experiments on the ISS',
          timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000)
        },
        {
          id: 'msg-4',
          role: 'assistant',
          content: 'The ISS has conducted numerous plant growth experiments through facilities like the Vegetable Production System (Veggie) and the Advanced Plant Habitat (APH). These experiments study how plants grow in microgravity, including changes in root orientation, water uptake, and cellular development. Notable successes include growing lettuce, radishes, and even cotton plants in space.',
          timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000 + 45000)
        }
      ]
    }
  ],
  messages: [],
  isLoading: false,
  setCurrentSession: (session) => set((state) => ({
    currentSession: session,
    messages: session ? session.messages : []
  })),
  addMessage: (message) =>
    set((state) => {
      const updatedMessages = [...state.messages, message];
      const updatedSessions = state.sessions.map(session =>
        session.id === state.currentSession?.id
          ? { ...session, messages: updatedMessages, updatedAt: new Date() }
          : session
      );
      return {
        messages: updatedMessages,
        sessions: updatedSessions,
        currentSession: state.currentSession
          ? { ...state.currentSession, messages: updatedMessages, updatedAt: new Date() }
          : null
      };
    }),
  clearMessages: () => set({ messages: [] }),
  setLoading: (loading) => set({ isLoading: loading }),
  createNewSession: () => {
    const newSession: ChatSession = {
      id: `session-${Date.now()}`,
      title: 'New Conversation',
      createdAt: new Date(),
      updatedAt: new Date(),
      messages: [],
    };
    set((state) => ({
      sessions: [newSession, ...state.sessions],
      currentSession: newSession,
      messages: [],
    }));
  },
  updateSessionTitle: (sessionId, title) =>
    set((state) => ({
      sessions: state.sessions.map(session =>
        session.id === sessionId ? { ...session, title } : session
      ),
      currentSession: state.currentSession?.id === sessionId
        ? { ...state.currentSession, title }
        : state.currentSession
    })),

  // Search
  searchFilters: {},
  setSearchFilters: (filters) => set({ searchFilters: filters }),
  clearSearchFilters: () => set({ searchFilters: {} }),
  // UI State
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
