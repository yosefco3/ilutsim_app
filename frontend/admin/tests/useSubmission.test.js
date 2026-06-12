import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useSubmission } from '../src/hooks/useSubmission';

// Mock guardApiClient
vi.mock('../src/api/guardApiClient', () => ({
  get: vi.fn(),
  post: vi.fn(),
}));

import { get, post } from '../src/api/guardApiClient';

describe('useSubmission', () => {
  const initData = 'test-init-data';

  beforeEach(() => {
    vi.resetAllMocks();
    // Reset window.location.href
    delete window.location;
    window.location = { href: '' };
  });

  it('should start in loading state', () => {
    get.mockResolvedValue({ data: null, error: 'no week' });

    const { result } = renderHook(() => useSubmission(initData));
    expect(result.current.loading).toBe(true);
  });

  it('should load week data and set canSubmit=true for open week', async () => {
    get.mockImplementation((path) => {
      if (path.includes('current-week')) {
        return Promise.resolve({
          data: {
            id: 'w1',
            status: 'open',
            week_label: 'שבוע 1',
            days: [{ day_index: 0, blocked: false }],
          },
          error: null,
        });
      }
      if (path.includes('my')) {
        return Promise.resolve({ data: null, error: null });
      }
      return Promise.resolve({ data: null, error: null });
    });

    const { result } = renderHook(() => useSubmission(initData));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.canSubmit).toBe(true);
    expect(result.current.weekStatus).toBe('open');
    expect(result.current.days).toHaveLength(1);
  });

  it('should set canSubmit=false for locked week', async () => {
    get.mockResolvedValue({
      data: { id: 'w1', status: 'locked', days: [] },
      error: null,
    });

    const { result } = renderHook(() => useSubmission(initData));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.canSubmit).toBe(false);
    expect(result.current.isLocked).toBe(true);
  });

  it('should toggle shift on a day', async () => {
    get.mockResolvedValue({
      data: { id: 'w1', status: 'open', days: [{ day_index: 0, blocked: false }] },
      error: null,
    });

    const { result } = renderHook(() => useSubmission(initData));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    act(() => {
      result.current.toggleShift(0, 'morning');
    });

    expect(result.current.days[0].shifts.morning.active).toBe(true);
  });

  it('should navigate to /submit/success on successful submit', async () => {
    get.mockResolvedValue({
      data: { id: 'w1', status: 'open', days: [{ day_index: 0, blocked: false }] },
      error: null,
    });
    post.mockResolvedValue({ data: { success: true }, error: null });

    const { result } = renderHook(() => useSubmission(initData));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.submit();
    });

    expect(window.location.href).toBe('/submit/success');
    expect(post).toHaveBeenCalledWith(
      expect.stringContaining('submissions'),
      expect.objectContaining({ week_id: 'w1' }),
      initData,
    );
  });

  it('should handle submit error', async () => {
    get.mockResolvedValue({
      data: { id: 'w1', status: 'open', days: [] },
      error: null,
    });
    post.mockResolvedValue({ data: null, error: 'שגיאה' });

    const { result } = renderHook(() => useSubmission(initData));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.submit();
    });

    expect(result.current.error).toBe('שגיאה');
  });
});