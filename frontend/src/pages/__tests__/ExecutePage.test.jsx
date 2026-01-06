import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import ExecutePage from '../ExecutePage';
import { useModelsStore, useExecutionStore } from '../../store';

vi.mock('../../store', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useModelsStore: vi.fn(),
      useExecutionStore: vi.fn(),
    };
  });

describe('ExecutePage', () => {
    beforeEach(() => {
        useModelsStore.mockReturnValue({
            models: [],
            selectedModel: null,
        });
        useExecutionStore.mockReturnValue({
            isExecuting: false,
            result: null,
        });
    });

  it('should render execute page components', () => {
    renderWithProviders(<ExecutePage />);
    expect(screen.getByPlaceholderText(/Enter your prompt/i)).toBeInTheDocument();
  });
});
