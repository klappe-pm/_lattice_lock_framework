import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import ModelsPage from '../ModelsPage';
import { useModelsStore } from '../../store';

vi.mock('../../store', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useModelsStore: vi.fn(),
    };
  });

describe('ModelsPage', () => {
    beforeEach(() => {
        useModelsStore.mockReturnValue({
            models: [],
            loading: false,
            fetchModels: vi.fn(),
        });
    });

  it('should render models page', () => {
    renderWithProviders(<ModelsPage />);
    // ModelsPage renders ModelRegistry which usually has "Models" header or similar
    // Assuming ModelRegistry has a button to add model or shows list
    expect(screen.getByText(/Manage Models/i)).toBeInTheDocument();
  });
});
