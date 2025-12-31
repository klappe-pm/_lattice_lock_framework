# Testing Guide

## Overview

This document provides comprehensive guidance on writing and running tests for the Lattice Lock Framework frontend application.

## Getting Started

### Running Tests

```bash
# Run tests in watch mode (recommended for development)
npm test

# Run tests once (CI mode)
npm run test:ci

# Generate coverage report
npm run test:coverage

# Open Vitest UI for visual test debugging
npm run test:ui
```

### Test Structure

Tests are organized alongside the code they test:

```
src/
├── components/
│   ├── models/
│   │   ├── ModelList.jsx
│   │   └── __tests__/
│   │       └── ModelList.test.jsx
│   └── ...
├── store/
│   ├── modelStore.js
│   └── __tests__/
│       └── modelStore.test.js
└── api/
    ├── modelsApi.js
    └── __tests__/
        └── modelsApi.test.js
```

## Writing Tests

### Component Tests

Use the custom `renderWithProviders` utility to render components with necessary context:

```javascript
import { renderWithProviders, screen, userEvent } from '../../test/utils';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    renderWithProviders(<MyComponent />);
    expect(screen.getByText(/expected text/i)).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    renderWithProviders(<MyComponent />);
    
    const button = screen.getByRole('button');
    await user.click(button);
    
    expect(screen.getByText(/clicked/i)).toBeInTheDocument();
  });
});
```

### Store Tests

Test Zustand stores by interacting with their state directly:

```javascript
import { useModelStore } from '../modelStore';
import { createMockModel } from '../../test/utils';

describe('modelStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useModelStore.getState().reset();
  });

  it('should add model', () => {
    const model = createMockModel({ id: '1' });
    useModelStore.getState().addModel(model);
    
    const state = useModelStore.getState();
    expect(state.models).toHaveLength(1);
    expect(state.models[0]).toEqual(model);
  });
});
```

### API Tests

Mock fetch or use MSW (Mock Service Worker) for API tests:

```javascript
import { vi } from 'vitest';
import { fetchModels } from '../modelsApi';

describe('modelsApi', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should fetch models successfully', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ models: [{ id: '1', name: 'Test' }] }),
    });

    const models = await fetchModels();
    expect(models).toHaveLength(1);
  });
});
```

## Test Utilities

### Mock Data Factories

Use the provided factories to create consistent test data:

```javascript
import { createMockModel, createMockTask, createMockExecution } from '../test/utils';

const model = createMockModel({ 
  id: 'custom-id', 
  name: 'Custom Model' 
});

const task = createMockTask({ 
  status: 'completed',
  progress: 100 
});

const execution = createMockExecution({ 
  status: 'failed',
  logs: ['Error occurred'] 
});
```

### Custom Render

The `renderWithProviders` function wraps components with:
- React Router's `BrowserRouter`
- Any Zustand stores (when configured)
- Other context providers (when added)

```javascript
import { renderWithProviders } from '../test/utils';

// Basic usage
renderWithProviders(<Component />);

// With custom router state
renderWithProviders(<Component />, {
  initialRouterEntries: ['/models', '/executions'],
});
```

### Async Utilities

Wait for loading states to complete:

```javascript
import { waitForLoadingToFinish } from '../test/utils';

it('should load data', async () => {
  renderWithProviders(<Component />);
  await waitForLoadingToFinish();
  expect(screen.getByText(/data loaded/i)).toBeInTheDocument();
});
```

## Best Practices

### 1. Test User Behavior, Not Implementation

❌ **Bad**: Testing internal state
```javascript
expect(component.state.count).toBe(1);
```

✅ **Good**: Testing visible behavior
```javascript
expect(screen.getByText('Count: 1')).toBeInTheDocument();
```

### 2. Use Accessible Queries

Prefer queries that mirror how users interact with your app:

```javascript
// Preferred (in order)
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/username/i)
screen.getByPlaceholderText(/search/i)
screen.getByText(/welcome/i)

// Avoid
screen.getByTestId('submit-button')
```

### 3. Test Error States

Always test error handling:

```javascript
it('should display error message on API failure', async () => {
  global.fetch.mockRejectedValueOnce(new Error('API Error'));
  
  renderWithProviders(<Component />);
  await waitForLoadingToFinish();
  
  expect(screen.getByText(/error occurred/i)).toBeInTheDocument();
});
```

### 4. Keep Tests Isolated

Each test should be independent:

```javascript
beforeEach(() => {
  // Reset mocks
  vi.clearAllMocks();
  
  // Reset stores
  useModelStore.getState().reset();
  
  // Clear localStorage
  localStorage.clear();
});
```

### 5. Use Descriptive Test Names

```javascript
// Good descriptive names
it('should display error when model name is empty')
it('should disable submit button during API call')
it('should redirect to dashboard after successful login')
```

## Accessibility Testing

Test keyboard navigation and screen reader support:

```javascript
it('should be keyboard accessible', async () => {
  const user = userEvent.setup();
  renderWithProviders(<Form />);
  
  // Tab through form fields
  await user.tab();
  expect(screen.getByLabelText(/username/i)).toHaveFocus();
  
  await user.tab();
  expect(screen.getByLabelText(/password/i)).toHaveFocus();
});

it('should have proper ARIA labels', () => {
  renderWithProviders(<Button />);
  const button = screen.getByRole('button');
  
  expect(button).toHaveAttribute('aria-label', 'Submit form');
});
```

## Coverage Guidelines

Aim for these coverage targets:

- **Statements**: 80%
- **Branches**: 75%
- **Functions**: 80%
- **Lines**: 80%

View coverage report:

```bash
npm run test:coverage
open coverage/index.html
```

## Common Patterns

### Testing Async Components

```javascript
it('should load and display data', async () => {
  renderWithProviders(<AsyncComponent />);
  
  // Wait for loading to finish
  await waitFor(() => {
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });
  
  expect(screen.getByText(/data loaded/i)).toBeInTheDocument();
});
```

### Testing Forms

```javascript
it('should submit form with valid data', async () => {
  const user = userEvent.setup();
  const mockOnSubmit = vi.fn();
  
  renderWithProviders(<Form onSubmit={mockOnSubmit} />);
  
  await user.type(screen.getByLabelText(/name/i), 'John Doe');
  await user.type(screen.getByLabelText(/email/i), 'john@example.com');
  await user.click(screen.getByRole('button', { name: /submit/i }));
  
  expect(mockOnSubmit).toHaveBeenCalledWith({
    name: 'John Doe',
    email: 'john@example.com',
  });
});
```

### Testing Conditional Rendering

```javascript
it('should show different content based on props', () => {
  const { rerender } = renderWithProviders(<Component isLoading={true} />);
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  rerender(<Component isLoading={false} />);
  expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  expect(screen.getByText(/content/i)).toBeInTheDocument();
});
```

## Troubleshooting

### Tests timing out

Increase timeout or check for unresolved promises:

```javascript
it('should complete', async () => {
  // ...
}, { timeout: 10000 }); // 10 second timeout
```

### Mock not working

Ensure mocks are set up before the test runs:

```javascript
beforeEach(() => {
  vi.mock('../api', () => ({
    fetchData: vi.fn().mockResolvedValue({ data: [] }),
  }));
});
```

### Coverage not updated

Clear coverage cache:

```bash
rm -rf coverage/
npm run test:coverage
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Vitest UI](https://vitest.dev/guide/ui.html)
