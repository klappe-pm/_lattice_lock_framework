import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import DashboardPage from '../DashboardPage';
import { useModelsStore, useProgressStore } from '../../store';

vi.mock('../../store', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useModelsStore: vi.fn(),
    useProgressStore: vi.fn(),
  };
});

describe('DashboardPage', () => {
    beforeEach(() => {
        useModelsStore.mockReturnValue({
            models: [],
            stats: { total: 0, online: 0, offline: 0 }
        });
        useProgressStore.mockReturnValue({
            tasks: [],
            tokenUsage: { total: 0 },
            cost: 0
        });
    });

  it('should render dashboard stats', () => {
    renderWithProviders(<DashboardPage />);
    expect(screen.getByText('Tasks Completed')).toBeInTheDocument();
    expect(screen.getByText('Tokens Used')).toBeInTheDocument();
  });
});
