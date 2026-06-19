import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WeekStatusControl from '../src/components/WeekStatusControl';

const noop = vi.fn();

function renderWeek(status, handlers = {}, auto = {}) {
  return render(
    <WeekStatusControl
      week={{ id: 'w1', status }}
      onOpen={handlers.onOpen || noop}
      onLock={handlers.onLock || noop}
      onPublish={handlers.onPublish || noop}
      loading={false}
      autoOpen={auto.autoOpen || { enabled: false }}
      autoLock={auto.autoLock || { enabled: false }}
    />,
  );
}

describe('WeekStatusControl', () => {
  it('never shows a delete button — removed to prevent accidental data loss', () => {
    for (const status of ['published', 'closed', 'open', 'locked']) {
      const { unmount } = renderWeek(status);
      expect(screen.queryByText(/מחק/)).not.toBeInTheDocument();
      unmount();
    }
  });

  it('offers "open for submission" on a closed week', () => {
    renderWeek('closed');
    expect(screen.getByText(/פתח להגשה/)).toBeInTheDocument();
  });

  it('does not crash on an unknown status (falls back)', () => {
    renderWeek('something-weird');
    // Badge still renders; no throw.
    expect(screen.getByText(/סגור/)).toBeInTheDocument();
  });

  it('does not publish immediately — asks for confirmation first', () => {
    const onPublish = vi.fn();
    renderWeek('locked', { onPublish });

    // Clicking "פרסם" opens a confirm dialog instead of publishing right away.
    fireEvent.click(screen.getByText(/📢/));
    expect(onPublish).not.toHaveBeenCalled();
    // The warning explains publish is irreversible (unlike lock).
    expect(screen.getByText(/בלתי הפיכה/)).toBeInTheDocument();
  });

  it('publishes only after confirming the irreversible warning', () => {
    const onPublish = vi.fn();
    renderWeek('locked', { onPublish });

    fireEvent.click(screen.getByText(/📢/));
    fireEvent.click(screen.getByText('כן, פרסם'));
    expect(onPublish).toHaveBeenCalledWith('w1');
  });

  it('cancelling the publish confirm does not publish', () => {
    const onPublish = vi.fn();
    renderWeek('locked', { onPublish });

    fireEvent.click(screen.getByText(/📢/));
    fireEvent.click(screen.getByText(/ביטול|בטל/));
    expect(onPublish).not.toHaveBeenCalled();
  });

  // ── automation gating ──────────────────────────────────────────────────────

  it('hides "open for submission" and shows an indicator when auto-open is on', () => {
    renderWeek('closed', {}, { autoOpen: { enabled: true, weekday: 'sunday', time: '07:00' } });
    expect(screen.queryByText(/פתח להגשה/)).not.toBeInTheDocument();
    expect(screen.getByText(/תיפתח אוטומטית/)).toBeInTheDocument();
    expect(screen.getByText(/ראשון 07:00/)).toBeInTheDocument();
  });

  it('hides "lock" and shows an indicator on an open week when auto-lock is on', () => {
    renderWeek('open', {}, { autoLock: { enabled: true, weekday: 'wednesday', time: '12:00' } });
    expect(screen.queryByText(/^נעל$/)).not.toBeInTheDocument();
    expect(screen.getByText(/תינעל אוטומטית/)).toBeInTheDocument();
    expect(screen.getByText(/רביעי 12:00/)).toBeInTheDocument();
  });

  it('keeps the manual buttons when both switches are off', () => {
    const { unmount } = renderWeek('closed');
    expect(screen.getByText(/פתח להגשה/)).toBeInTheDocument();
    unmount();
    renderWeek('open');
    expect(screen.getByText(/נעל/)).toBeInTheDocument();
  });

  it('always keeps "publish" on a locked week, even with automation on', () => {
    renderWeek(
      'locked',
      {},
      { autoOpen: { enabled: true, weekday: 'sunday', time: '07:00' },
        autoLock: { enabled: true, weekday: 'wednesday', time: '12:00' } },
    );
    expect(screen.getByText(/📢/)).toBeInTheDocument();
    // manual open is hidden on locked when auto-open is on
    expect(screen.queryByText(/פתח להגשה/)).not.toBeInTheDocument();
  });
});
