# Frontend Plan

## Lattice Lock Framework - Frontend Architecture and Recommendations

This document outlines the frontend architecture assessment, accessibility evaluation, performance analysis, and recommended improvements.

## Current State

### Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.3 | UI framework |
| Vite | 7.3.0 | Build tool and dev server |
| React Router | 7.11.0 | Client-side routing |
| ReactFlow | 11.11.4 | Flow diagram visualization |
| Zustand | 5.0.9 | State management |
| MDUI | 2.1.4 | Material Design UI components |
| D3 | 7.9.0 | Data visualization |
| Socket.io Client | 4.8.3 | Real-time communication |

### Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Route-level components
│   ├── store/           # Zustand state stores
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Root component
│   └── main.jsx         # Entry point
├── public/              # Static assets
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
├── eslint.config.js     # ESLint configuration
└── vitest.config.js     # Test configuration
```

### Lines of Code

| File Type | Count | Lines |
|-----------|-------|-------|
| JavaScript/JSX | 3,457 | 5,029 |
| CSS | ~10 | ~500 |
| JSON | ~5 | ~200 |

## Identified Issues

### Issue 1: Dependency Version Conflicts (P1)

**Location:** `frontend/package.json`

**Problem:** npm reports invalid versions for multiple packages:
```
@vitest/coverage-v8@2.1.9 invalid: "^4.0.16" from the root project
@vitest/ui@2.1.9 invalid: "^4.0.16" from the root project
globals@16.5.0 invalid: "^17.0.0" from the root project
jsdom@25.0.1 invalid: "^27.4.0" from the root project
vitest@2.1.9 invalid: "^4.0.16" from the root project
```

**Impact:** Tests may fail, build may be unreliable

**Fix:**
```json
{
  "devDependencies": {
    "vitest": "^2.1.9",
    "@vitest/coverage-v8": "^2.1.9",
    "@vitest/ui": "^2.1.9",
    "globals": "^16.5.0",
    "jsdom": "^25.0.1"
  }
}
```

### Issue 2: Missing Accessibility Testing (P4)

**Location:** `frontend/`

**Problem:** No accessibility testing configured (axe-core, pa11y, etc.)

**Impact:** Accessibility issues may go undetected, potential ADA compliance issues

**Fix:** Add accessibility testing:
```bash
npm install --save-dev @axe-core/react vitest-axe
```

### Issue 3: No Error Boundary (P3)

**Location:** `frontend/src/`

**Problem:** No React Error Boundary component for graceful error handling

**Impact:** Unhandled errors crash entire application

**Fix:** Add Error Boundary component:
```jsx
// src/components/ErrorBoundary.jsx
import { Component } from 'react';

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h1>Something went wrong</h1>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Issue 4: Missing Loading States (P3)

**Location:** `frontend/src/`

**Problem:** No consistent loading state handling across components

**Impact:** Poor user experience during data fetching

**Fix:** Create loading component and hook:
```jsx
// src/components/LoadingSpinner.jsx
export const LoadingSpinner = ({ size = 'medium' }) => (
  <div className={`loading-spinner loading-spinner--${size}`}>
    <mdui-circular-progress />
  </div>
);

// src/hooks/useAsync.js
import { useState, useCallback } from 'react';

export const useAsync = (asyncFunction) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await asyncFunction(...args);
      setData(result);
      return result;
    } catch (e) {
      setError(e);
      throw e;
    } finally {
      setLoading(false);
    }
  }, [asyncFunction]);

  return { loading, error, data, execute };
};
```

## Architecture Recommendations

### 1. Component Organization

**Current:** Flat component structure  
**Recommended:** Feature-based organization

```
frontend/src/
├── features/
│   ├── dashboard/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── store/
│   │   └── index.js
│   ├── models/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── index.js
│   └── settings/
│       ├── components/
│       └── index.js
├── shared/
│   ├── components/
│   ├── hooks/
│   └── utils/
└── App.jsx
```

### 2. State Management

**Current:** Zustand stores  
**Recommendation:** Keep Zustand, add persistence

```javascript
// src/store/settingsStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useSettingsStore = create(
  persist(
    (set) => ({
      theme: 'light',
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'lattice-settings',
    }
  )
);
```

### 3. API Layer

**Recommendation:** Create centralized API client

```javascript
// src/api/client.js
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8080';

class APIClient {
  async request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new APIError(response.status, await response.text());
    }
    
    return response.json();
  }

  get(endpoint) {
    return this.request(endpoint);
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const api = new APIClient();
```

## Accessibility Recommendations

### 1. Add ARIA Labels

```jsx
// Before
<button onClick={handleClick}>
  <Icon name="settings" />
</button>

// After
<button 
  onClick={handleClick}
  aria-label="Open settings"
>
  <Icon name="settings" aria-hidden="true" />
</button>
```

### 2. Keyboard Navigation

```jsx
// Add keyboard support to custom components
const handleKeyDown = (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleClick();
  }
};

<div 
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={handleKeyDown}
>
  Click me
</div>
```

### 3. Focus Management

```jsx
// Manage focus for modals
import { useEffect, useRef } from 'react';

const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef();
  
  useEffect(() => {
    if (isOpen) {
      modalRef.current?.focus();
    }
  }, [isOpen]);
  
  return isOpen ? (
    <div 
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      {children}
    </div>
  ) : null;
};
```

## Performance Recommendations

### 1. Code Splitting

```jsx
// Use React.lazy for route-level code splitting
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./features/dashboard'));
const Models = lazy(() => import('./features/models'));

const App = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/models" element={<Models />} />
    </Routes>
  </Suspense>
);
```

### 2. Memoization

```jsx
// Memoize expensive components
import { memo, useMemo } from 'react';

const ModelList = memo(({ models, filter }) => {
  const filteredModels = useMemo(
    () => models.filter(m => m.name.includes(filter)),
    [models, filter]
  );
  
  return (
    <ul>
      {filteredModels.map(model => (
        <ModelItem key={model.id} model={model} />
      ))}
    </ul>
  );
});
```

### 3. Virtual Scrolling

```jsx
// For large lists, use virtualization
import { useVirtualizer } from '@tanstack/react-virtual';

const VirtualList = ({ items }) => {
  const parentRef = useRef();
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });
  
  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {items[virtualItem.index]}
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Testing Recommendations

### 1. Component Testing

```jsx
// src/components/__tests__/Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 2. Accessibility Testing

```jsx
// src/components/__tests__/Button.a11y.test.jsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'vitest-axe';
import { Button } from '../Button';

expect.extend(toHaveNoViolations);

describe('Button accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

## Implementation Roadmap

### Phase 1: Fix Critical Issues (1 day)
1. Fix dependency version conflicts
2. Run `npm install` to regenerate lock file
3. Verify tests pass

### Phase 2: Add Error Handling (2 days)
4. Add Error Boundary component
5. Add loading states
6. Add API error handling

### Phase 3: Accessibility (1 week)
7. Add axe-core testing
8. Audit existing components for ARIA
9. Add keyboard navigation
10. Add focus management

### Phase 4: Performance (1 week)
11. Add code splitting
12. Add memoization to heavy components
13. Add virtual scrolling for lists
14. Add performance monitoring

### Phase 5: Testing (1 week)
15. Increase test coverage to 80%
16. Add accessibility tests
17. Add integration tests
18. Add visual regression tests

## Verification Checklist

- [ ] All npm dependencies install without errors
- [ ] All tests pass
- [ ] No accessibility violations (axe-core)
- [ ] Lighthouse performance score > 90
- [ ] Lighthouse accessibility score > 90
- [ ] Error boundaries catch and display errors gracefully
- [ ] Loading states shown during data fetching
- [ ] Keyboard navigation works throughout app
