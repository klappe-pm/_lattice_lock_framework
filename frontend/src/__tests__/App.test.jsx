import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App', () => {
  it('should render dashboard by default', () => {
    render(<App />);
    // Check for main Dashboard header
    expect(screen.getByRole('heading', { name: /Dashboard/i, level: 1 })).toBeInTheDocument();
  });

  it('should render navigation sidebar', () => {
    render(<App />);
    // Check for navigation links (may appear in sidebar and quick actions)
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Models').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Execute').length).toBeGreaterThan(0);
  });

  it('should render quick actions', () => {
    render(<App />);
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('New Prompt')).toBeInTheDocument();
  });
});
