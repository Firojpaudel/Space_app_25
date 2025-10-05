import { render, screen } from '@testing-library/react';
import MessageBubble from '@/components/chat/MessageBubble';
import { Message } from '@/types';

describe('MessageBubble', () => {
  const mockUserMessage: Message = {
    id: '1',
    role: 'user',
    content: 'Test message',
    timestamp: new Date(),
  };

  const mockAssistantMessage: Message = {
    id: '2',
    role: 'assistant',
    content: 'Test response',
    timestamp: new Date(),
    sources: [
      {
        id: 's1',
        title: 'Test Source',
        score: 0.95,
        type: 'publication',
      },
    ],
  };

  it('renders user message correctly', () => {
    render(<MessageBubble message={mockUserMessage} />);
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('renders assistant message with sources', () => {
    render(<MessageBubble message={mockAssistantMessage} />);
    expect(screen.getByText('Test response')).toBeInTheDocument();
    expect(screen.getByText(/Test Source/)).toBeInTheDocument();
  });

  it('applies correct styling for user messages', () => {
    const { container } = render(<MessageBubble message={mockUserMessage} />);
    const bubble = container.querySelector('.bg-accent-200');
    expect(bubble).toBeInTheDocument();
  });
});
