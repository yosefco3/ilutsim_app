import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAdminConstraints } from '../src/hooks/useAdminConstraints';

vi.mock('../src/api/adminApiClient', () => ({
  fetchGuard: vi.fn(),
  fetchWeeks: vi.fn(),
  fetchUserSubmissions: vi.fn(),
  createGuardSubmission: vi.fn(),
}));

vi.mock('../src/api/guardApiClient.js', () => ({
  get: vi.fn(),
}));

import {
  fetchGuard,
  fetchWeeks,
  fetchUserSubmissions,
  createGuardSubmission,
} from '../src/api/adminApiClient';
import { get as guardGet } from '../src/api/guardApiClient.js';

describe('useAdminConstraints', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    fetchGuard.mockResolvedValue({ id: 'g1', first_name: 'דנה', last_name: 'כהן' });
    fetchWeeks.mockResolvedValue([
      { id: 'w1', status: 'open', week_label: 'שבוע 1', start_date: '2025-06-01' },
      { id: 'w2', status: 'closed', week_label: 'שבוע 2', start_date: '2025-06-08' },
    ]);
    fetchUserSubmissions.mockResolvedValue([]);
    guardGet.mockResolvedValue({ data: null, error: 'x' });
    createGuardSubmission.mockResolvedValue({ id: 's1' });
  });

  it('loads guard + weeks and defaults to the open week with 7 day rows', async () => {
    const { result } = renderHook(() => useAdminConstraints('g1'));

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.guard.first_name).toBe('דנה');
    expect(result.current.weeks).toHaveLength(2);
    expect(result.current.selectedWeekId).toBe('w1'); // the open week

    await waitFor(() => expect(result.current.days).toHaveLength(7));
  });

  it('pre-fills an existing submission for the selected week', async () => {
    fetchUserSubmissions.mockResolvedValue([
      {
        week_id: 'w1',
        general_notes: 'הערה',
        days: [
          {
            date: '2025-06-01', // day_index 0
            shift_windows: [
              { shift_type: 'morning', start_time: '07:00:00', end_time: '15:00:00' },
            ],
          },
        ],
      },
    ]);

    const { result } = renderHook(() => useAdminConstraints('g1'));
    await waitFor(() => expect(result.current.days).toHaveLength(7));

    const day0 = result.current.days.find((d) => d.day_index === 0);
    expect(day0.shifts.morning.active).toBe(true);
    expect(day0.shifts.morning.from_hour).toBe('07:00');
    expect(result.current.notes).toBe('הערה');
  });

  it('builds the payload with user_id + week_id and only active shifts', async () => {
    const { result } = renderHook(() => useAdminConstraints('g1'));
    await waitFor(() => expect(result.current.days).toHaveLength(7));

    act(() => result.current.toggleShift(2, 'night'));
    await act(async () => {
      await result.current.submit();
    });

    expect(createGuardSubmission).toHaveBeenCalledTimes(1);
    const payload = createGuardSubmission.mock.calls[0][0];
    expect(payload.user_id).toBe('g1');
    expect(payload.week_id).toBe('w1');

    const day2 = payload.days.find((d) => d.day_index === 2);
    expect(day2.shifts).toHaveLength(1);
    expect(day2.shifts[0].shift_type).toBe('night');

    // Untouched days carry no active shifts
    const day0 = payload.days.find((d) => d.day_index === 0);
    expect(day0.shifts).toHaveLength(0);

    expect(result.current.saved).toBe(true);
  });
});
