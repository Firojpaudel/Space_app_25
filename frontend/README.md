# K-OSMOS Frontend

Modern Next.js 14 + React 18 frontend for the K-OSMOS Space Biology Knowledge Engine.

## 🎨 Design System

### Color Palette

**Dark Mode:**
- Background: `#101010`
- Cards: `#1A1A1A`
- Text: `#E6E6E6`

**Light Mode:**
- Background: `#F5F5F5`
- Cards: `#EAEAEA`
- Text: `#1A1A1A`

**Accent Colors (Green Theme):**
- `#0B3D0B` - Darkest green
- `#1A4314` - Dark green
- `#2E8B57` - Medium green
- `#3CB371` - Light green
- `#66CDAA` - Lightest green

### Typography

- **Font:** Space Grotesk (Google Fonts)
- **Weights:** 300, 400, 500, 600, 700

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Python backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home/Chat page
│   ├── search/            # Search page
│   ├── analytics/         # Analytics dashboard
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── chat/             # Chat interface components
│   ├── search/           # Search components
│   ├── analytics/        # Analytics/charts
│   ├── layout/           # Layout components
│   └── providers/        # Context providers
├── store/                # Zustand state management
├── utils/                # Utility functions & API
├── types/                # TypeScript definitions
├── __tests__/            # Jest tests
└── public/               # Static assets
```

## 🧩 Key Components

### Chat Interface
- **ChatInterface:** Main chat container
- **MessageBubble:** Individual message display with markdown support
- **InputBox:** Message input with voice/file attachment
- **EntityHighlight:** Extracted entity visualization
- **SourcesPanel:** Citation and source display

### Search
- **SearchFilters:** Mission, organism, tissue filters
- **SearchResults:** Paginated search results with relevance scores

### Analytics
- **TrendsChart:** Time-series research trends
- **MissionComparison:** Bar chart comparison
- **EntityDistribution:** Pie chart of organisms/entities

### Layout
- **Navbar:** Fixed top navigation with theme toggle
- **Sidebar:** Collapsible navigation sidebar
- **ThemeProvider:** Dark/light mode context

## 🎯 Features

### Core Functionality
- ✅ Real-time chat with AI assistant
- ✅ Semantic search across 1,175+ resources
- ✅ Entity extraction and highlighting
- ✅ Source citation tracking
- ✅ Session management
- ✅ Dark/light mode
- ✅ Responsive design

### UI/UX Highlights
- Grammarly-inspired minimal interface
- Smooth transitions and animations
- Contextual popovers
- Inline entity highlights
- Floating action buttons
- Loading skeletons
- Sticky toolbars

## 🔌 Backend Integration

The frontend communicates with the Python backend via REST API:

### API Endpoints

**Chat:**
- `POST /api/chat` - Send message, get AI response
- `POST /api/chat/session` - Create new session
- `GET /api/chat/history/{id}` - Get chat history

**Search:**
- `POST /api/search` - Semantic search
- `POST /api/search/semantic` - Vector similarity search

**Analytics:**
- `GET /api/analytics/trends` - Research trends
- `POST /api/analytics/missions` - Mission comparison
- `GET /api/analytics/entities` - Entity distribution

**Entities:**
- `POST /api/entities/extract` - Extract biological entities

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm test -- --coverage
```

### Test Structure
- Component tests in `__tests__/components/`
- Utility tests in `__tests__/utils/`
- Uses Jest + React Testing Library

## 🏗️ Building for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

## 🎨 Styling

Uses **Tailwind CSS** with custom configuration:

### Custom Classes
- `.card` - Card container
- `.card-hover` - Card with hover effect
- `.btn-primary` - Primary button
- `.btn-secondary` - Secondary button
- `.entity-organism` - Organism highlight
- `.entity-tissue` - Tissue highlight
- `.citation-badge` - Citation tag

### Animations
- `animate-fade-in` - Fade in effect
- `animate-slide-up` - Slide up effect
- `animate-scale-in` - Scale in effect

## 📦 Dependencies

### Core
- `next` - Next.js framework
- `react` - React library
- `zustand` - State management
- `axios` - HTTP client

### UI
- `tailwindcss` - Utility CSS
- `lucide-react` - Icon library
- `framer-motion` - Animations
- `react-plotly.js` - Charts

### Content
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub flavored markdown

## 🔧 Development

### Code Style
- ESLint configured for Next.js
- TypeScript strict mode
- Component-based architecture
- Custom hooks for reusability

### State Management
Uses Zustand for:
- Theme preferences
- Chat sessions and messages
- Search filters
- UI state (sidebar, modals)

### Performance
- Server-side rendering (SSR)
- Client-side caching
- Lazy loading for heavy components
- Image optimization with Next.js

## 🐛 Troubleshooting

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start Python backend
cd ../
python api_server.py
```

### Port Conflicts
```bash
# Change port in package.json
next dev -p 3001
```

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Zustand](https://github.com/pmndrs/zustand)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for NASA Space Apps Challenge 2025**
