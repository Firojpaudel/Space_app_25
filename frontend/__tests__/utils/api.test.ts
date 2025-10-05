import { chatAPI, searchAPI } from '@/utils/api';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('chatAPI', () => {
    it('sends message successfully', async () => {
      const mockResponse = {
        data: {
          response: 'Test response',
          sources: [],
          entities: [],
        },
      };

      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValue(mockResponse as any);

      const result = await chatAPI.sendMessage('Test message');
      expect(result.response).toBe('Test response');
    });
  });

  describe('searchAPI', () => {
    it('performs search successfully', async () => {
      const mockResults = [
        {
          id: '1',
          title: 'Test Result',
          content: 'Test content',
          sourceType: 'publication',
          score: 0.9,
          metadata: {},
        },
      ];

      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValue({ data: mockResults } as any);

      const results = await searchAPI.search('test query');
      expect(results).toHaveLength(1);
      expect(results[0].title).toBe('Test Result');
    });
  });
});
