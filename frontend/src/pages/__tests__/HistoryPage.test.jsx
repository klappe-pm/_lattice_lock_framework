import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import HistoryPage from '../HistoryPage';
import { useExecutionStore } from '../../store';

vi.mock('../../store', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useExecutionStore: vi.fn(),
    };
  });

describe('HistoryPage', () => {
    beforeEach(() => {
        useExecutionStore.mockReturnValue({
            history: [],
            fetchHistory: vi.fn(),
            clearHistory: vi.fn(),
        });
    });

  it('should render history page empty state', () => {
    renderWithProviders(<HistoryPage />);
    expect(screen.getByText(/No history found/i)).toBeInTheDocument();
  });
});
