import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders, screen } from '../../test/utils';
import SettingsPage from '../SettingsPage';

describe('SettingsPage', () => {
  it('should render settings sections', () => {
    renderWithProviders(<SettingsPage />);
    expect(screen.getByText(/General Settings/i)).toBeInTheDocument();
    expect(screen.getByText(/API Keys/i)).toBeInTheDocument();
  });
});
