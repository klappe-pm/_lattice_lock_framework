import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import ProjectsPage from '../ProjectsPage';
import { useProjectsStore } from '../../store';

vi.mock('../../store', async (importOriginal) => {
    const actual = await importOriginal();
    return {
      ...actual,
      useProjectsStore: vi.fn(),
    };
  });

describe('ProjectsPage', () => {
    beforeEach(() => {
        useProjectsStore.mockReturnValue({
            projects: [],
            activeProject: null,
            loading: false,
            fetchProjects: vi.fn(),
        });
    });

  it('should render project list', () => {
    renderWithProviders(<ProjectsPage />);
    // ProjectsPage renders ProjectList by default route
    expect(screen.getByText(/Projects/i)).toBeInTheDocument();
  });
});
