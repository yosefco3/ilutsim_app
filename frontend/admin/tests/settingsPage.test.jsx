import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

vi.mock('../src/hooks/useSettings', () => ({
  useSettings: vi.fn(),
}));
vi.mock('../src/api/adminApiClient', () => ({
  applyTelegramToken: vi.fn(),
}));

import { useSettings } from '../src/hooks/useSettings';
import { applyTelegramToken } from '../src/api/adminApiClient';
import SettingsPage from '../src/pages/SettingsPage';

function mockHook(overrides = {}) {
  useSettings.mockReturnValue({
    settings: [
      { key: 'min_nights', value: '2', description: null },
      { key: 'telegram_bot_token', value: 'secret', description: null },
    ],
    draft: { min_nights: '2', telegram_bot_token: 'secret' },
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
    applyTelegramToken.mockReset();
    mockHook();
  });

  it('renders Hebrew labels, not raw keys', () => {
    render(<SettingsPage />);
    expect(screen.getByText('מינימום לילות')).toBeInTheDocument();
    expect(screen.queryByText('min_nights')).not.toBeInTheDocument();
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

  it('applies a telegram token and shows the bot username on success', async () => {
    applyTelegramToken.mockResolvedValue({ ok: true, bot_username: 'safra_bot' });
    render(<SettingsPage />);

    fireEvent.change(screen.getByPlaceholderText('הדבק טוקן חדש'), {
      target: { value: '123:abc' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'החל טוקן' }));

    await waitFor(() => expect(applyTelegramToken).toHaveBeenCalledWith('123:abc'));
    await waitFor(() =>
      expect(screen.getByText(/safra_bot/)).toBeInTheDocument(),
    );
  });

  it('shows an error when the token apply fails', async () => {
    applyTelegramToken.mockRejectedValue(new Error('טוקן לא תקין'));
    render(<SettingsPage />);

    fireEvent.change(screen.getByPlaceholderText('הדבק טוקן חדש'), {
      target: { value: 'bad' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'החל טוקן' }));

    await waitFor(() => expect(screen.getByText('טוקן לא תקין')).toBeInTheDocument());
  });
});
