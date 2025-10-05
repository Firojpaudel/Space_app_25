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
  const [datasetSearch, setDatasetSearch] = useState('');
  const [publicationSearch, setPublicationSearch] = useState('');
  const [selectedDatasetFilter, setSelectedDatasetFilter] = useState('');
  const [selectedJournalFilter, setSelectedJournalFilter] = useState('');

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
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">OSDR Datasets</h3>
                <span className="text-xs bg-accent-200 text-white px-2 py-1 rounded-full">567</span>
              </div>
              
              {/* Search Box */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search datasets..."
                  value={datasetSearch}
                  onChange={(e) => setDatasetSearch(e.target.value)}
                  className="w-full text-xs px-3 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-200 text-gray-900 dark:text-gray-100"
                />
              </div>

              {/* Filter Tags */}
              <div className="flex flex-wrap gap-1">
                {['Microgravity', 'Plant Biology', 'Bone Density', 'Cardiovascular'].map((tag) => (
                  <button
                    key={tag}
                    onClick={() => setSelectedDatasetFilter(selectedDatasetFilter === tag ? '' : tag)}
                    className={`text-xs px-2 py-1 rounded-full smooth-transition ${
                      selectedDatasetFilter === tag
                        ? 'bg-accent-200 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 hover:bg-accent-200 hover:text-white'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>

              {/* Dataset List */}
              <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                {[
                  {
                    id: 'GLDS-104',
                    title: 'Microgravity Effects on Mouse Liver',
                    organism: 'Mus musculus',
                    samples: 48,
                    mission: 'STS-131',
                    type: 'RNA-Seq'
                  },
                  {
                    id: 'GLDS-251',
                    title: 'Plant Growth in Microgravity',
                    organism: 'Arabidopsis thaliana',
                    samples: 24,
                    mission: 'ISS Expedition 39',
                    type: 'Transcriptomics'
                  },
                  {
                    id: 'GLDS-173',
                    title: 'Bone Density Changes in Spaceflight',
                    organism: 'Rattus norvegicus',
                    samples: 36,
                    mission: 'STS-135',
                    type: 'Proteomics'
                  },
                  {
                    id: 'GLDS-321',
                    title: 'Cardiovascular Adaptation Study',
                    organism: 'Homo sapiens',
                    samples: 12,
                    mission: 'ISS Expedition 45',
                    type: 'Clinical Data'
                  },
                  {
                    id: 'GLDS-189',
                    title: 'Muscle Atrophy in Zero-G',
                    organism: 'Mus musculus',
                    samples: 60,
                    mission: 'SpaceX CRS-8',
                    type: 'RNA-Seq'
                  }
                ].map((dataset) => (
                  <button
                    key={dataset.id}
                    onClick={() => {
                      // Simulate opening dataset details
                      alert(`Opening dataset ${dataset.id}: ${dataset.title}\n\nOrganism: ${dataset.organism}\nSamples: ${dataset.samples}\nMission: ${dataset.mission}\nType: ${dataset.type}`);
                    }}
                    className="w-full p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-left smooth-transition border border-transparent hover:border-accent-200"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono bg-accent-200 text-white px-2 py-0.5 rounded">
                            {dataset.id}
                          </span>
                          <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded">
                            {dataset.type}
                          </span>
                        </div>
                        <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate mb-1">
                          {dataset.title}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                          <span>{dataset.organism}</span>
                          <span>{dataset.samples} samples</span>
                        </div>
                        <p className="text-xs text-accent-200 mt-1">{dataset.mission}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-bold text-accent-200">127</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">RNA-Seq</div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-bold text-accent-200">89</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Proteomics</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'publications' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Publications</h3>
                <span className="text-xs bg-accent-200 text-white px-2 py-1 rounded-full">608+</span>
              </div>

              {/* Search Box */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search papers..."
                  value={publicationSearch}
                  onChange={(e) => setPublicationSearch(e.target.value)}
                  className="w-full text-xs px-3 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-200 text-gray-900 dark:text-gray-100"
                />
              </div>

              {/* Journal Filters */}
              <div className="flex flex-wrap gap-1">
                {['Nature', 'Science', 'Cell', 'PNAS', 'Acta Astronautica'].map((journal) => (
                  <button
                    key={journal}
                    onClick={() => setSelectedJournalFilter(selectedJournalFilter === journal ? '' : journal)}
                    className={`text-xs px-2 py-1 rounded-full smooth-transition ${
                      selectedJournalFilter === journal
                        ? 'bg-accent-200 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 hover:bg-accent-200 hover:text-white'
                    }`}
                  >
                    {journal}
                  </button>
                ))}
              </div>

              {/* Publications List */}
              <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                {[
                  {
                    title: 'Microgravity-induced bone loss in astronauts',
                    authors: 'Smith, J. et al.',
                    journal: 'Nature Medicine',
                    year: 2023,
                    citations: 127,
                    impact: 'High',
                    doi: '10.1038/s41591-023-02456-1'
                  },
                  {
                    title: 'Plant gravitropism mechanisms in space',
                    authors: 'Chen, L. et al.',
                    journal: 'Science',
                    year: 2023,
                    citations: 89,
                    impact: 'High',
                    doi: '10.1126/science.abq7890'
                  },
                  {
                    title: 'Cardiovascular adaptation during long-duration spaceflight',
                    authors: 'Rodriguez, M. et al.',
                    journal: 'Circulation',
                    year: 2022,
                    citations: 156,
                    impact: 'Medium',
                    doi: '10.1161/CIRCULATIONAHA.122.059876'
                  },
                  {
                    title: 'Muscle atrophy countermeasures in microgravity',
                    authors: 'Johnson, K. et al.',
                    journal: 'Journal of Applied Physiology',
                    year: 2022,
                    citations: 73,
                    impact: 'Medium',
                    doi: '10.1152/japplphysiol.00234.2022'
                  },
                  {
                    title: 'Space radiation effects on cellular DNA repair',
                    authors: 'Williams, A. et al.',
                    journal: 'Cell',
                    year: 2023,
                    citations: 201,
                    impact: 'High',
                    doi: '10.1016/j.cell.2023.04.012'
                  }
                ].map((paper, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      // Simulate opening paper details
                      window.open(`https://doi.org/${paper.doi}`, '_blank');
                    }}
                    className="w-full p-3 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-left smooth-transition border border-transparent hover:border-accent-200"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-gray-900 dark:text-gray-100 leading-tight mb-1">
                            {paper.title}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                            {paper.authors}
                          </p>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-accent-200 font-medium">{paper.journal}</span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">({paper.year})</span>
                          </div>
                        </div>
                        <div className={`text-xs px-2 py-0.5 rounded-full ${
                          paper.impact === 'High' 
                            ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                            : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300'
                        }`}>
                          {paper.impact}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-500 dark:text-gray-400">
                          {paper.citations} citations
                        </span>
                        <span className="font-mono text-gray-400 dark:text-gray-500">
                          DOI: {paper.doi.split('/').pop()}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              {/* Publication Stats */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-bold text-accent-200">2023</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Latest Year</div>
                </div>
                <div className="text-center p-2 bg-gray-50 dark:bg-gray-800 rounded">
                  <div className="text-sm font-bold text-accent-200">8.4</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Avg Impact</div>
                </div>
              </div>

              {/* Hidden Gem */}
              <div className="p-2 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <p className="text-xs text-green-700 dark:text-green-300">
                  <strong>Hidden Gem:</strong> The most cited space biology paper has over 2,000 citations and studies bone loss mechanisms!
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
                {sessions.slice(0, 6).map((session, index) => (
                  <button
                    key={session.id}
                    onClick={() => {
                      setCurrentSession(session);
                      setActiveTab('chat');
                    }}
                    className="w-full p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer smooth-transition text-left"
                  >
                    <div className="flex justify-between items-start gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">
                          {session.title}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(session.updatedAt).toLocaleDateString()}
                          </span>
                          <span className="text-xs text-accent-200">{session.messages.length} messages</span>
                        </div>
                      </div>
                    </div>
                  </button>
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
