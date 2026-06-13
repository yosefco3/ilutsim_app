import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WeekStatusControl from '../src/components/WeekStatusControl';

const noop = vi.fn();

function renderWeek(status, handlers = {}) {
  return render(
    <WeekStatusControl
      week={{ id: 'w1', status }}
      onOpen={handlers.onOpen || noop}
      onLock={handlers.onLock || noop}
      onPublish={handlers.onPublish || noop}
      loading={false}
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
});
