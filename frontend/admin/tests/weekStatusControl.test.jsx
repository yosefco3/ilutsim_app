import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import WeekStatusControl from '../src/components/WeekStatusControl';

const noop = vi.fn();

function renderWeek(status) {
  return render(
    <WeekStatusControl
      week={{ id: 'w1', status }}
      onOpen={noop}
      onLock={noop}
      onPublish={noop}
      onDelete={noop}
      loading={false}
    />,
  );
}

describe('WeekStatusControl', () => {
  it('hides the delete button for a published week', () => {
    renderWeek('published');
    expect(screen.queryByText(/מחק/)).not.toBeInTheDocument();
  });

  it('shows the delete button for a closed week', () => {
    renderWeek('closed');
    expect(screen.getByText(/מחק/)).toBeInTheDocument();
  });

  it('shows the delete button for an open week', () => {
    renderWeek('open');
    expect(screen.getByText(/מחק/)).toBeInTheDocument();
  });

  it('offers "open for submission" on a closed week', () => {
    renderWeek('closed');
    expect(screen.getByText(/פתוח להגשה/)).toBeInTheDocument();
  });

  it('does not crash on an unknown status (falls back)', () => {
    renderWeek('something-weird');
    // Badge still renders; no throw.
    expect(screen.getByText(/מחק/)).toBeInTheDocument();
  });
});
