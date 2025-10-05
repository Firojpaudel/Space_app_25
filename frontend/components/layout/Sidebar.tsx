'use client';

import { useStore } from '@/store/useStore';
import {
  MessageSquare,
  Database,
  BookOpen,
  BarChart3,
  Settings,
  History,
  Plus,
} from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { icon: MessageSquare, label: 'Chat', id: 'chat' },
  { icon: Database, label: 'Datasets', id: 'datasets' },
  { icon: BookOpen, label: 'Publications', id: 'publications' },
  { icon: BarChart3, label: 'Analytics', id: 'analytics' },
  { icon: History, label: 'History', id: 'history' },
  { icon: Settings, label: 'Settings', id: 'settings' },
];

export default function Sidebar() {
  const { sidebarOpen, sessions, currentSession, setCurrentSession, createNewSession, theme, setTheme } =
    useStore();
  const [activeTab, setActiveTab] = useState('chat');

  if (!sidebarOpen) return null;

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 smooth-transition z-30 shadow-lg">
      <div className="flex flex-col h-full text-gray-900 dark:text-gray-100">
        {/* Navigation Tabs */}
        <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-3 gap-1 p-2">
            {navItems.slice(0, 3).map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 p-2 rounded-lg smooth-transition ${
                  activeTab === item.id
                    ? 'bg-accent-200/10 text-accent-200'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="text-xs font-medium">{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
          {activeTab === 'chat' && (
            <div className="space-y-3">
              <button
                onClick={createNewSession}
                className="w-full flex items-center gap-2 px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-accent-200 dark:hover:border-accent-200 hover:bg-accent-200/5 smooth-transition"
              >
                <Plus className="w-4 h-4" />
                <span className="font-medium">New Conversation</span>
              </button>

              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider px-2">
                  Recent Chats
                </h3>
                {sessions.map((session) => (
                  <button
                    key={session.id}
                    onClick={() => setCurrentSession(session)}
                    className={`w-full text-left px-3 py-2 rounded-lg smooth-transition ${
                      currentSession?.id === session.id
                        ? 'bg-accent-200/10 border border-accent-200'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{session.title}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(session.updatedAt).toLocaleDateString()}
                        </p>
                      </div>
                      <MessageSquare className="w-4 h-4 flex-shrink-0 text-gray-400" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'datasets' && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold mb-3">OSDR Datasets</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                567 NASA experimental datasets available
              </p>
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-xs text-blue-700 dark:text-blue-300">
                  <strong>Space Fact:</strong> NASA has collected more data about space than there are grains of sand on Earth's beaches!
                </p>
              </div>
            </div>
          )}

          {activeTab === 'publications' && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold mb-3">Publications</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                608+ peer-reviewed papers indexed
              </p>
              <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <p className="text-xs text-green-700 dark:text-green-300">
                  <strong>Hidden Gem:</strong> The first academic paper about "space sickness" was titled "Mal de l'espace" - French for "space sickness"!
                </p>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold mb-3">Research Analytics</h3>
              
              {/* Query Statistics */}
              <div className="space-y-3">
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Most Searched Topics</span>
                  </div>
                  <div className="space-y-2">
                    {[
                      { topic: 'Microgravity effects', count: 45, percentage: 85 },
                      { topic: 'ISS experiments', count: 32, percentage: 60 },
                      { topic: 'Bone density', count: 28, percentage: 52 },
                      { topic: 'Plant growth', count: 19, percentage: 35 }
                    ].map((item, index) => (
                      <div key={index} className="flex items-center justify-between text-xs">
                        <span className="text-gray-700 dark:text-gray-300">{item.topic}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                            <div 
                              className="bg-accent-200 h-1.5 rounded-full" 
                              style={{ width: `${item.percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-gray-500 dark:text-gray-400 w-6">{item.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Research Trends */}
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                  <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Research Trends</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="text-center p-2 bg-white dark:bg-gray-700 rounded">
                      <div className="text-lg font-bold text-accent-200">127</div>
                      <div className="text-gray-500 dark:text-gray-400">Total Queries</div>
                    </div>
                    <div className="text-center p-2 bg-white dark:bg-gray-700 rounded">
                      <div className="text-lg font-bold text-accent-200">89%</div>
                      <div className="text-gray-500 dark:text-gray-400">Success Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold mb-3">Search History</h3>
              
              <div className="space-y-2">
                {[
                  { query: 'Effects of microgravity on bone density', time: '2 hours ago', results: 12 },
                  { query: 'ISS cardiovascular research studies', time: '5 hours ago', results: 8 },
                  { query: 'Plant growth experiments in space', time: '1 day ago', results: 15 },
                  { query: 'Muscle atrophy during spaceflight', time: '2 days ago', results: 9 },
                  { query: 'Space radiation effects on DNA', time: '3 days ago', results: 11 },
                  { query: 'Astronaut sleep patterns in microgravity', time: '1 week ago', results: 6 }
                ].map((item, index) => (
                  <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer smooth-transition">
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">
                          {item.query}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500 dark:text-gray-400">{item.time}</span>
                          <span className="text-xs text-accent-200">{item.results} results</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full text-xs text-accent-200 hover:text-accent-100 py-2 text-center">
                View All History
              </button>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold mb-3">Settings</h3>
              
              <div className="space-y-3">
                {/* Theme Setting */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Theme</span>
                  <select 
                    value={theme}
                    onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
                    className="text-xs bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-gray-900 dark:text-gray-100"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </select>
                </div>

                {/* Search Preferences */}
                <div className="space-y-2">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Search Preferences</span>
                  <div className="space-y-1">
                    {[
                      { label: 'Include experimental data', checked: true },
                      { label: 'Show confidence scores', checked: false },
                      { label: 'Auto-save searches', checked: true },
                      { label: 'Enable notifications', checked: false }
                    ].map((setting, index) => (
                      <label key={index} className="flex items-center gap-2 text-xs">
                        <input 
                          type="checkbox" 
                          defaultChecked={setting.checked}
                          className="w-3 h-3 text-accent-200 rounded"
                        />
                        <span className="text-gray-600 dark:text-gray-400">{setting.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Data Export */}
                <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                  <button className="w-full text-xs bg-accent-200 hover:bg-accent-100 text-white py-2 px-3 rounded smooth-transition">
                    Export Search Data
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom Actions */}
        <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-3">
          <div className="grid grid-cols-3 gap-2">
            {navItems.slice(3).map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 p-2 rounded-lg smooth-transition ${
                  activeTab === item.id
                    ? 'bg-accent-200/10 text-accent-200'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span className="text-xs">{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
