import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

vi.mock('../src/hooks/useSettings', () => ({
  useSettings: vi.fn(),
}));

import { useSettings } from '../src/hooks/useSettings';
import SettingsPage from '../src/pages/SettingsPage';

function mockHook(overrides = {}) {
  useSettings.mockReturnValue({
    settings: [
      { key: 'min_guard_coverage', value: '2', description: null },
      { key: 'telegram_bot_token', value: 'secret', description: null },
    ],
    draft: { min_guard_coverage: '2', telegram_bot_token: 'secret' },
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
    expect(screen.getByText('כיסוי שומרים מינימלי')).toBeInTheDocument();
    expect(screen.queryByText('min_guard_coverage')).not.toBeInTheDocument();
  });

  it('hides the telegram_bot_token secret from the generic list', () => {
    render(<SettingsPage />);
    expect(screen.queryByDisplayValue('secret')).not.toBeInTheDocument();
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
