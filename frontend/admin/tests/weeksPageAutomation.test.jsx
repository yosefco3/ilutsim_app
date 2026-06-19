import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('../src/hooks/useWeeks', () => ({ useWeeks: vi.fn() }));
vi.mock('../src/hooks/useSettings', () => ({ useSettings: vi.fn() }));

import { useWeeks } from '../src/hooks/useWeeks';
import { useSettings } from '../src/hooks/useSettings';
import WeeksPage from '../src/pages/WeeksPage';

function mockWeeks() {
  useWeeks.mockReturnValue({
    weeks: [{ id: 'w1', status: 'closed', start_date: '2026-06-21', end_date: '2026-06-27' }],
    loading: false,
    setStatus: vi.fn(),
    openForSubmission: vi.fn(),
    publish: vi.fn(),
  });
}

function mockSettings(list) {
  useSettings.mockReturnValue({ settings: list, loading: false });
}

const enabledSettings = [
  { key: 'auto_open_enabled', value: 'true' },
  { key: 'auto_open_weekday', value: 'sunday' },
  { key: 'auto_open_time', value: '07:00' },
  { key: 'auto_lock_enabled', value: 'true' },
  { key: 'auto_lock_weekday', value: 'wednesday' },
  { key: 'auto_lock_time', value: '12:00' },
];

const disabledSettings = [
  { key: 'auto_open_enabled', value: 'false' },
  { key: 'auto_lock_enabled', value: 'false' },
];

describe('WeeksPage automation banner', () => {
  beforeEach(() => {
    useWeeks.mockReset();
    useSettings.mockReset();
    mockWeeks();
  });

  it('shows a summary banner when automation is on', () => {
    mockSettings(enabledSettings);
    render(<WeeksPage />);
    const banner = screen.getByText(/🤖/);
    expect(banner).toBeInTheDocument();
    expect(banner.textContent).toContain('ראשון 07:00');
    expect(banner.textContent).toContain('רביעי 12:00');
    expect(banner.textContent).toContain('ידני'); // publish is always manual
  });

  it('shows no banner when both switches are off', () => {
    mockSettings(disabledSettings);
    render(<WeeksPage />);
    expect(screen.queryByText(/🤖/)).not.toBeInTheDocument();
  });

  it('waits for settings before rendering (no flicker)', () => {
    useSettings.mockReturnValue({ settings: [], loading: true });
    render(<WeeksPage />);
    // Spinner shown, week cards not yet rendered.
    expect(screen.queryByText(/📅/)).not.toBeInTheDocument();
  });
});
