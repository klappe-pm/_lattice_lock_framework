import { describe, it, expect, vi } from 'vitest';
import { createMockTask, renderWithProviders, screen } from '../../../test/utils';
import TaskList from '../TaskList';
import { useProgressStore } from '../../../store';

vi.mock('../../../store', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useProgressStore: vi.fn(),
  };
});

describe('TaskList', () => {
  it('should render empty state when no tasks', () => {
    // Mock empty store
    useProgressStore.mockReturnValue({
      tasks: [],
      tokenUsage: { total: 0 },
      cost: 0
    });
    
    renderWithProviders(<TaskList />);
    expect(screen.getByText(/No tasks yet/i)).toBeInTheDocument();
  });

  it('should render list of tasks', () => {
    const tasks = [
      createMockTask({ id: '1', name: 'Task 1', status: 'completed' }),
      createMockTask({ id: '2', name: 'Task 2', status: 'running' }),
    ];

    useProgressStore.mockReturnValue({
      tasks,
      tokenUsage: { total: 100 },
      cost: 0.001
    });

    renderWithProviders(<TaskList />);
    
    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });

  it('should show progress bar for running tasks', () => {
    const task = createMockTask({ status: 'running', progress: 50 });
    
    useProgressStore.mockReturnValue({
      tasks: [task],
      tokenUsage: { total: 50 },
      cost: 0.0005
    });

    renderWithProviders(<TaskList />);
    
    // TaskList calculates overall progress based on completed/total count, 
    // so 1 running task = 0% overall progress.
    // Individual task component shows indeterminate bar for running state, no text percentage.
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    // Verify progress bar container exists
    const progressBars = document.getElementsByClassName('progress-linear-indeterminate');
    expect(progressBars.length).toBeGreaterThan(0); 
  });
});
