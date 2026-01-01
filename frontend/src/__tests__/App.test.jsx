import { describe, it, expect } from 'vitest';
import { renderWithProviders, screen } from '../test/utils';
import App from '../App';

describe('App', () => {
  it('should render without crashing', () => {
    renderWithProviders(<App />);
    expect(screen.getByText(/Vite \+ React/i)).toBeInTheDocument();
  });

  it('should display Vite and React logos', () => {
    renderWithProviders(<App />);
    const logos = screen.getAllByRole('img');
    expect(logos).toHaveLength(2);
    expect(logos[0]).toHaveAttribute('alt', 'Vite logo');
    expect(logos[1]).toHaveAttribute('alt', 'React logo');
  });

  it('should display count button with initial value 0', () => {
    renderWithProviders(<App />);
    const button = screen.getByRole('button', { name: /count is 0/i });
    expect(button).toBeInTheDocument();
  });

  it('should increment count when button is clicked', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();
    
    renderWithProviders(<App />);
    const button = screen.getByRole('button', { name: /count is 0/i });
    
    await user.click(button);
    expect(screen.getByRole('button', { name: /count is 1/i })).toBeInTheDocument();
    
    await user.click(button);
    expect(screen.getByRole('button', { name: /count is 2/i })).toBeInTheDocument();
  });

  it('should have working links', () => {
    renderWithProviders(<App />);
    const links = screen.getAllByRole('link');
    
    expect(links[0]).toHaveAttribute('href', 'https://vite.dev');
    expect(links[0]).toHaveAttribute('target', '_blank');
    
    expect(links[1]).toHaveAttribute('href', 'https://react.dev');
    expect(links[1]).toHaveAttribute('target', '_blank');
  });

  it('should display instructional text', () => {
    renderWithProviders(<App />);
    expect(screen.getByText('Edit', { exact: false })).toBeInTheDocument();
    expect(screen.getByText('src/App.jsx')).toBeInTheDocument();
    expect(screen.getByText('and save to test HMR', { exact: false })).toBeInTheDocument();
    expect(screen.getByText(/Click on the Vite and React logos to learn more/i)).toBeInTheDocument();
  });
});
