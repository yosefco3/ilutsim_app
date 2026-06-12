import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

vi.mock('../src/hooks/useSettings', () => ({
  useSettings: vi.fn(),
}));

import { useSettings } from '../src/hooks/useSettings';
import SettingsPage from '../src/pages/SettingsPage';

function mockHook(overrides = {}) {
  useSettings.mockReturnValue({
    settings: [{ key: 'min_nights', value: '2', description: null }],
    draft: { min_nights: '2' },
    loading: false,
    saving: false,
    error: null,
    dirty: false,
    setValue: vi.fn(),
    save: vi.fn().mockResolvedValue(true),
    ...overrides,
  });
}

describe('SettingsPage', () => {
  beforeEach(() => {
    useSettings.mockReset();
    mockHook();
  });

  it('renders Hebrew labels, not raw keys', () => {
    render(<SettingsPage />);
    expect(screen.getByText('מינימום לילות')).toBeInTheDocument();
    expect(screen.queryByText('min_nights')).not.toBeInTheDocument();
  });

  it('does not render any telegram bot token field', () => {
    render(<SettingsPage />);
    expect(screen.queryByText('בוט טלגרם')).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'החל טוקן' })).not.toBeInTheDocument();
  });

  it('save button is disabled until dirty', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('button', { name: 'שמור' })).toBeDisabled();
  });

  it('clicking save calls the hook save()', async () => {
    const save = vi.fn().mockResolvedValue(true);
    mockHook({ dirty: true, save });
    render(<SettingsPage />);

    fireEvent.click(screen.getByRole('button', { name: 'שמור' }));
    await waitFor(() => expect(save).toHaveBeenCalled());
  });
});
