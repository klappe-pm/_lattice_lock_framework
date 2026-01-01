import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

/**
 * Custom render function that wraps components with necessary providers
 * @param {React.ReactElement} ui - Component to render
 * @param {Object} options - Render options
 * @param {Object} options.initialRouterEntries - Initial router location(s)
 * @param {Object} options.providerProps - Props to pass to providers
 * @returns {Object} - RTL render result with additional utilities
 */
export function renderWithProviders(ui, options = {}) {
  const { initialRouterEntries = ['/'], providerProps = {}, ...renderOptions } = options;

  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        {children}
      </BrowserRouter>
    );
  }

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}

/**
 * Wait for loading states to finish
 * @param {number} timeout - Maximum time to wait (ms)
 * @returns {Promise<void>}
 */
export async function waitForLoadingToFinish(timeout = 3000) {
  const { waitFor } = await import('@testing-library/react');
  await waitFor(
    () => {
      const loadingElements = document.querySelectorAll('[aria-busy="true"], [data-testid*="loading"]');
      if (loadingElements.length > 0) {
        throw new Error('Still loading');
      }
    },
    { timeout }
  );
}

/**
 * Create a mock Zustand store for testing
 * @param {Function} createStore - Zustand store creator
 * @param {Object} initialState - Initial state override
 * @returns {Object} - Mock store
 */
export function createMockStore(createStore, initialState = {}) {
  const store = createStore();
  const originalState = store.getState();
  store.setState({ ...originalState, ...initialState });
  return store;
}

/**
 * Mock model data factory
 * @param {Object} overrides - Property overrides
 * @returns {Object} - Mock model object
 */
export function createMockModel(overrides = {}) {
  return {
    id: 'model-1',
    name: 'Test Model',
    provider: 'openai',
    version: '1.0.0',
    capabilities: ['chat', 'completion'],
    status: 'active',
    ...overrides,
  };
}

/**
 * Mock task data factory
 * @param {Object} overrides - Property overrides
 * @returns {Object} - Mock task object
 */
export function createMockTask(overrides = {}) {
  return {
    id: 'task-1',
    name: 'Test Task',
    status: 'pending',
    progress: 0,
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

/**
 * Mock execution data factory
 * @param {Object} overrides - Property overrides
 * @returns {Object} - Mock execution object
 */
export function createMockExecution(overrides = {}) {
  return {
    id: 'execution-1',
    taskId: 'task-1',
    modelId: 'model-1',
    status: 'running',
    startedAt: new Date().toISOString(),
    logs: [],
    ...overrides,
  };
}

// Re-export everything from React Testing Library
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
